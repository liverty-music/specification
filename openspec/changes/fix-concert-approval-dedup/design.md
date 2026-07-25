## Context

Discovery → staging → approval is a three-stage pipeline. Each stage dedups on a
different key, and two of those keys are values that drift between discovery runs:

| Stage | Dedup / identity key | Stable? |
| --- | --- | --- |
| Search (`FilterNew` vs events & pending staged) | `(local_event_date, listed_venue_name, start_at)` — raw scraped string | No — Gemini name drift |
| Staged unique index | `(artist_id, local_date, resolved_place_id)` or `(…, listed_venue_name)` | Partly |
| Venue identity | `google_place_id` **and** `(listed_venue_name, admin_area)` — two independent partial-unique indexes | No — Places returns multiple `place_id`s per venue |
| Event natural key | `(venue_id, local_event_date, start_at)` `NULLS NOT DISTINCT` | Yes — resolved |

Because the read-side dedup keys differ from the write-side unique constraints, the
approval pipeline fails to recognise a venue/event it already created:

- **`already_exists`**: `resolveOrCreateVenue` looks up a venue by `place_id` only;
  when Places resolved a *different* `place_id` for an existing venue, the lookup
  misses and the subsequent `INSERT` collides on `idx_venues_listed_name_admin_area`.
  Confirmed in prod: 和歌山ビッグホエール exists as `place_id=ChIJGSP2Ti…` but the
  staged rows resolved to `ChIJizoipyy…`.
- **`failed_precondition`**: `FilterNew` compares the raw scraped `listed_venue_name`
  against the stored event's (drifted) `listed_venue_name`; a formatting difference
  (`フェスティバルホール` vs `大阪・フェスティバルホール`) defeats the match, so the
  concert is re-staged, and approval then finds the event already exists at the
  resolved `(venue_id, date, start_at)` and returns zero inserts. 16 of 19 prod
  collision rows show this exact name drift; 18 of 19 are the same artist.

Constraints: no DB migration is needed — every constraint and index already exists.
The admin `Approve` RPC change requires a specification release → BSR codegen before
backend/frontend can consume the generated types.

## Goals / Non-Goals

**Goals:**
- Approving a concert whose venue already exists never crashes on a unique violation.
- Approving a concert whose event already exists gives the reviewer a clear choice
  (keep existing vs adopt staged) instead of a dead-end error.
- Name-drift re-discoveries are recognised before staging, so the queue stops
  accumulating unapprovable duplicates.

**Non-Goals:**
- Canonical venue de-duplication / merging of already-split venue rows (two rows for
  the same physical place). That is a separate data-cleanup effort.
- Reconciling venue identity itself in the approval dialog — the duplicate-event
  reconciliation only touches the event's venue display name and NULL-only start/open
  fill; `venue_id`/`place_id` and the shared series title are fixed.
- Field-level merge in the reconciliation dialog — record-level choice only.
- Resolving start-time drift (same show discovered with a different `start_at`,
  which currently yields a *distinct* event rather than a duplicate).
- Catching a duplicate whose existing event belongs to a *different* artist at the same
  venue and date. The discovery dedup (`FilterNew`) runs against `ListByArtist`, which is
  per-artist, so a cross-artist same-venue-date collision is invisible to D2 regardless of
  name normalization; the event natural key plus D3 reconciliation at approval are its only
  backstop. (Observed once in the prod snapshot: 神戸国際会館.)
- Retroactively clearing the existing stale staged rows. D2 only prevents *future*
  name-drift re-staging; the ~19 rows already queued are cleared through the D3
  reconciliation path or manual review (see Migration Plan / tasks).

## Decisions

### D1 — Venue resolution is idempotent get-or-create, `place_id`-authoritative

`resolveOrCreateVenue` resolves in this order:

1. If `resolved_place_id` is set, `GetByPlaceID`. Hit → return it.
2. On miss (or no `place_id`), `GetByListedName(listed_venue_name, admin_area)`. Hit → return it.
3. Neither → `INSERT … ON CONFLICT DO NOTHING`. If it inserted, return the new id.
4. If `ON CONFLICT` suppressed the insert (lost race, or either unique index fired),
   re-SELECT by `place_id` then by `(listed_venue_name, admin_area)` and return the winner.

Rationale: `place_id` is the more canonical identity when present, but it is not
reliable (proven multi-CID case), so `(listed_venue_name, admin_area)` — the identity
the DB already enforces as unique — is the fallback. `ON CONFLICT DO NOTHING` with no
target (not a named constraint) absorbs a violation on *either* partial-unique index,
which a single-target clause cannot. The re-SELECT makes it race-safe.

- **`admin_area` symmetry**: the lookup in step 2 and the `INSERT` in step 3 MUST derive
  `admin_area` identically (`resolved_admin_area ?? admin_area`). Today the lookup uses
  the raw value while the insert prefers the resolved value — an asymmetry that itself
  produces miss-then-collide.
- **`place_id` backfill**: when step 2 finds a venue with a NULL `place_id` and the
  staged row carries a resolved `place_id`, backfill it. Never overwrite a non-NULL
  `place_id` (that could collide on `idx_venues_google_place_id`).

Alternatives considered: making `place_id` the single source of truth and dropping the
`(listed_venue_name, admin_area)` unique index. Rejected — it would let the 和歌山
multi-CID case create two venue rows for one physical place, and it needs a migration +
data backfill. The two-key get-or-create keeps both safety nets.

### D2 — Discovery dedup matches on a stable venue identity

`FilterNew` (and the pending-staged dedup) SHALL compare venues on a normalized
identity rather than the raw `listed_venue_name` string, so `フェスティバルホール` and
`大阪・フェスティバルホール` collapse to the same venue and the second discovery is
recognised as already-known.

Two mechanisms are viable; the implementation chooses per cost:
- **(a) Normalize the name** before comparison (trim, full/half-width fold, strip
  leading `〈admin_area〉・` / `〈city〉公演 ＠` prefixes). Cheap, no extra API calls,
  but heuristic.
- **(b) Resolve venue first, dedup by `venue_id`.** Authoritative, but moves the Places
  call ahead of dedup, increasing API cost for concerts that turn out to be duplicates.

Decision: prefer (a) as the primary matcher (no added API cost, catches the observed
drift), and keep the existing `(date, start_at)` component unchanged. (b) is a fallback
only if normalization proves insufficient; record the choice in tasks. Either way the
event natural key `(venue_id, …)` remains the final DB-level safety net.

### D3 — Duplicate event → reviewer reconciliation, not `failed_precondition`

When approval detects an existing event at the resolved `(venue_id, local_event_date,
start_at)` (the two current zero-insert paths: exact-start duplicate, and unknown-start
staged vs known-start existing), the `Approve` RPC returns a **duplicate-conflict**
result carrying the existing event's display fields. The reviewer picks record-level:

- **KEEP_EXISTING** → append the staged row to the rejection log with a duplicate
  reason, delete the staged row. Auditable, mirrors a normal reject.
- **ADOPT_STAGED** → overwrite the existing event's `listed_venue_name` from the staged
  row, and fill `start_at`/`open_at` only where the existing value is NULL (a known time is
  never nulled out — `title` lives on the shared `series` row and is out of scope, and the
  unknown-start-staged case must not erase a known start); leave `venue_id`/`place_id`
  untouched; delete the staged row.

The duplicate conflict is only about which *display representation* to keep — both sides
already resolve to the same `venue_id` (that is how the duplicate was detected), so the
reconciliation never touches venue identity (keeps D1's scope separate from D3).

### D4 — `Approve` RPC shape: one idempotent RPC, two phases

`Approve` gains an optional `resolution` enum (`RESOLUTION_UNSPECIFIED`,
`KEEP_EXISTING`, `ADOPT_STAGED`). First call omits it; if a duplicate is detected the
response carries a `conflict` message (existing event fields + staged preview) and does
not mutate. The console shows the dialog and re-calls `Approve` with the chosen
`resolution`. Rationale: keeps the surface to one RPC, stays idempotent, and avoids a
separate `ResolveConflict` verb that would duplicate the staged-id + lookup plumbing.

Alternative considered: a dedicated `ResolveConflict` RPC. Rejected for surface bloat;
the two-phase `Approve` carries no more state and reads naturally in the console.

### D5 — Rollout order

`already_exists` is a live prod crash and its fix (D1) needs no proto change, so it and
the discovery-dedup fix (D2) ship first as backend-only PRs. The reconciliation (D3/D4)
carries a schema change and follows the Cross-Repo Release Coordination protocol:
specification PR → release → BSR codegen → backend + frontend consume generated types.
All three are tracked in this single change; tasks are ordered so the backend-only
fixes are not blocked on BSR.

## Risks / Trade-offs

- **Name normalization is heuristic (D2a)** → keep the event natural key as the DB-level
  final safety net; if a duplicate still slips through, D3 reconciliation catches it at
  approval instead of crashing. Log normalization decisions for tuning.
- **ADOPT_STAGED overwrites a curated event's display fields** → scope the overwrite to
  display fields only (never identity), and require an explicit reviewer choice; default
  (unspecified) never mutates an existing event.
- **`place_id` backfill could collide on `idx_venues_google_place_id`** → backfill only
  when the existing row's `place_id` is NULL; wrap in the same `ON CONFLICT`-tolerant
  path so a concurrent backfill degrades to a no-op.
- **Two-phase `Approve` race** (staged row changes between phases) → the second call
  re-reads the staged row and re-checks the conflict; if the staged row is gone, the
  existing idempotent "already approved" success path applies.
- **BSR gap** (backend/frontend can't build until codegen) → prepare downstream branches
  against planned types with a swap TODO; open PRs only after the package upgrade.

## Migration Plan

No DB migration. Deploy order: (1) backend PR with D1+D2 (backend-only) → release → prod
verify 和歌山 approves and stale duplicates dedup; (2) specification PR with D4 schema →
release → BSR codegen; (3) backend PR consuming the `resolution`/`conflict` fields
(D3/D4) + frontend PR with the dialog → releases → prod verify reconciliation end to end.
Rollback: each PR is independently revertible; the two-phase `Approve` degrades to the
current behavior if `resolution` is ignored, and D1 only broadens venue lookup so it is
safe to revert to the insert-only path. Blast radius of D1 is small: `VenueRepository.Create`
has a single caller (`createVenueFromStaged` on the approval path — confirmed), so the
discovery/staging pipeline is unaffected by the create-path change.

## Open Questions

- D2: confirm during implementation whether name normalization (a) alone clears the
  observed prod drift, or whether resolve-first-then-dedup (b) is needed for a subset.
- Whether to run a one-off cleanup pass over the existing ~19 stale staged rows via the
  new reconciliation path, or let reviewers clear them manually post-deploy.
