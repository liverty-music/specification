## Context

See proposal.md — Why. Today every discovered concert is staged and manually approved.
The new-vs-conflict decision (`detectDuplicateEvent`) currently runs at **approval time**,
inside `concertUseCase.Approve` (`internal/usecase/concert_admin_uc.go`), because it needs a
resolved `venue_id` (get-or-create), and venue rows are only created on approval. The
`CONCERT.discovered` consumer (`internal/usecase/concert_creation_uc.go`) only resolves the
venue via Google Places and denormalizes preview fields onto a `staged_concert` row.

Key existing pieces this change reuses unchanged:
- `resolveOrCreateVenue`, `detectDuplicateEvent`, `buildAndInsertConcerts`, and the
  `resolveExistingEvent` fill logic in the admin usecase.
- The two-source discovery dedup `FilterNew` in `internal/usecase/concert_uc.go`.
- The unchanged `Approve` reconciliation (`KeepExisting` / `AdoptStaged`) for staged conflicts.

## Goals / Non-Goals

**Goals:**
- Move the new-vs-conflict branch from approval time into the `CONCERT.discovered` consumer.
- Auto-publish new concerts (insert + `CONCERT.created`) without a staged row.
- Keep staged rows + `Approve` reconciliation for same-slot conflicts only.
- Add a suppression concept keyed by natural key; consult it in `FilterNew`; write it on `Delete`.

**Non-Goals:**
- Changing the conflict definition (still same-slot `(venue_id, local_event_date, start_at)`).
- Changing `Approve` reconciliation semantics.
- A per-concert Gemini confidence gate (grounding confidence is unreliable per prior findings).
- **Provenance tracking or a dedicated review surface.** No `origin` / auto-publish-timestamp is
  recorded and no "recently auto-published" review view is built. Retraction reuses the existing
  full-catalog admin `List` + `Delete`; suppression makes the deletion durable. This keeps the change
  backend-only (no proto/BSR change, no frontend work). A proactive review/audit surface can be a
  separate follow-up if search quality ever regresses.
- An un-suppress UI beyond a minimal operator escape hatch (can be a follow-up).

## Decisions

**1. Branch point lives in the discovery consumer, reusing the admin usecase helpers.**
The consumer first resolves the venue via Google Places. **A concert whose venue does not resolve
(`place == nil`) is staged, never auto-published** — see Decision 6. For a resolved venue it calls
`resolveOrCreateVenue` → suppression gate (Decision 4) → `detectDuplicateEvent`. A suppressed resolved
key short-circuits to skip (no publish, no stage). Otherwise: `nil` → `buildAndInsertConcerts` + publish
`CONCERT.created`; conflict → upsert `staged_concert` (today's staging path). This keeps one canonical
duplicate-detection implementation and avoids drift between discovery and approval.
*Alternative considered:* keep the branch at approval and add an "auto-approve" flag — rejected;
it still forces every concert through the queue table and a second processing hop.

**2. Venue row is created only on the auto-publish path.** A conflict resolves to the existing
event's venue, so `resolveOrCreateVenue` returns an existing row (no insert) whenever a conflict is
detected; a brand-new venue implies no existing event there, i.e. the new/publish path. This
preserves the "no orphan venues for never-published concerts" guarantee without extra bookkeeping.

**3. No provenance tracking; retraction reuses the existing admin surface.** An earlier draft stored
which events were auto-published (an `origin` marker + auto-publish timestamp) to power a "recently
auto-published" review view. That was cut: it forced a workflow concern onto either the pure
physical-identity `events` table or a new side table, plus an admin `List` proto change (the shared
`entity.v1.Concert` DTO is fan-facing, so exposing origin there — or wrapping it admin-side — added
either DTO pollution or a breaking change), plus frontend work and a full BSR release cycle. The
retraction path already exists: admin `List` returns the full published catalog and `Delete` removes
any concert. The only durable piece the safety net actually needs is **suppression** (Decision 4), and
suppression is origin-agnostic — it keys on the deleted event's natural key regardless of how the
event was published. So no `origin`/timestamp is recorded, no `events` column or side table is added
for provenance, and no proto/frontend change is required. *Trade-off:* the loss is *proactive*
detection of a bad auto-published concert; retraction becomes reactive (catalog spot-check, fan
report). Accepted given improved search quality; a review/audit surface can be a clean follow-up that
does not touch this change's core.

**4. Suppression is its own table, not the rejection log; the check runs in the consumer.** New
`suppressed_concerts` keyed by the **event** natural key `(venue_id, local_event_date, start_at)` with
`NULLS NOT DISTINCT` on `start_at` to mirror the `events` unique key exactly. The suppression check runs
in the discovery **consumer**, right after `resolveOrCreateVenue` yields the `venue_id` — the only point
where the full `(venue_id, local_event_date, start_at)` key exists. (`FilterNew` in `executeSearch` runs
*before* venue resolution, keyed on `(local_date, listed_venue_name)`, so it structurally cannot consult
a venue-keyed table; the suppression gate must sit after resolution.) When the resolved key matches a
`suppressed_concerts` row, the consumer skips the concert entirely — it neither auto-publishes nor stages
it, mirroring the existing published/pending exclusions but at the resolved-key layer. `Delete` writes a
suppression row inside the same transaction as the cascade delete. The `rejected_concerts_log` stays
analysis-only. *Alternative:*
reuse the rejection log with a "suppress" flag — rejected; the spec explicitly keeps that log
non-suppressing and analysis-only, and conflating the two invites accidental suppression.
*Un-suppress:* delete the `suppressed_concerts` row (minimal operator path; UI optional follow-up).

**5. Suppression key granularity matches the event-level deletion, and applies regardless of origin.**
`Delete` removes an entire event `(venue_id, local_event_date, start_at)` by cascade, independent of
performing artist, so the suppression key is the same triple — no `artist_id`. This prevents a
co-headliner's per-artist discovery from resurrecting a physical slot the operator deleted. Suppression
applies to every deletion regardless of how the event was originally published (auto-published or
developer-approved): a deleted concert must not silently return via auto-publish on the next discovery
run. The deleted event already carries `venue_id`/`local_event_date`/`start_at`, so the suppression row is
derived directly from it — no Google Places call at delete. *Alternative considered:* key by
`(artist_id, venue_id, local_event_date, start_at)` to match the per-artist discovery model — rejected
as weaker than the deletion granularity (a different performer could resurrect the slot).

**6. Auto-publish requires a resolved venue; an unresolved venue is staged for review.** When Google
Places cannot resolve the scraped venue name (`place == nil`), the consumer stages the concert exactly
as today rather than auto-publishing it. Auto-publishing an unresolved venue would mint a `venues` row
from the raw listed name with no `place_id` and **no coordinates**, which (a) silently excludes the
concert from proximity / HypeNearby matching so follower push can be missed, and (b) publishes a venue
whose accuracy was never reviewed. Auto-publish is for *confident* new concerts; an unresolved venue is
inherently unconfident, so it keeps the human gate. This also preserves the existing "no orphan
`venues` rows for never-published concerts" guarantee on the unresolved path, since staging creates no
`venues` row. *Note:* a resolved venue that turns out to be a same-slot conflict is still staged (per
Decision 1) — "resolved" is necessary for auto-publish, not sufficient.

## Risks / Trade-offs

- **Auto-publishing the least-anchored data** → New concerts have no existing counterpart to
  validate against, yet they now publish and notify without review. Mitigation: delete-with-suppression
  is the safety net (retract via the existing admin `List` + `Delete`); immediate notification is an
  accepted product decision.
- **No proactive detection of a bad auto-published concert** → With the review view cut, there is no
  dedicated surface that highlights recently auto-published concerts; an operator finds a bad row
  reactively (full-catalog spot-check, fan report). Accepted deliberately: search quality is now
  sufficient, and a review/audit surface can be added later as an isolated follow-up without touching
  this change.
- **Immediate push for a hallucinated concert cannot be recalled** → Accepted. Mitigation: deleting the
  concert suppresses re-creation so the mistake is not compounded on later discovery runs.
- **Dead deep-link after deletion** → A push already delivered may deep-link to a deleted event.
  Mitigation: the concert-detail deep-link path degrades gracefully to a "no longer available" state
  (existing deeplink-push handling).
- **Suppression breaks the "re-discovery is idempotent / non-permanent" philosophy** → Intentional and
  scoped: suppression is a deliberate operator signal, reversible only via the un-suppress path,
  and kept separate from the non-suppressing rejection log.
- **Co-headliner / different-performer-same-slot** → If artist A auto-publishes an event and artist B
  is later discovered at the same `(venue, date, start)`, B is detected as a conflict and staged;
  today's `AdoptStaged` does not add B as a performer. This is a pre-existing reconciliation gap that
  auto-publish may surface more often; out of scope here, noted for a follow-up.
- **Heavier consumer** → The consumer now does venue get-or-create + an event lookup per discovered
  concert (previously only Places resolution). Acceptable: discovery is a batched CronJob, not a hot
  path.

## Migration Plan

1. Atlas migration: create `suppressed_concerts`. No change to `events`; no backfill.
2. Backend: move the branch into the consumer; `Delete` writes suppression; `FilterNew` consults it.
   Ship behind the discovery consumer so behavior only changes on the next discovery run.
3. Rollback: revert the consumer branch to always-stage; the new table is inert if unused.

This is a backend-only change: no proto/BSR schema change and no frontend work, so no cross-repo
release coordination — a single backend PR plus the migration.
