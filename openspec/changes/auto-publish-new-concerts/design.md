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
- Mark published events with origin + auto-publish time; expose on admin `List`.
- Add a suppression concept keyed by natural key; consult it in `FilterNew`; write it on `Delete`.

**Non-Goals:**
- Changing the conflict definition (still same-slot `(venue_id, local_event_date, start_at)`).
- Changing `Approve` reconciliation semantics.
- A per-concert Gemini confidence gate (grounding confidence is unreliable per prior findings).
- An un-suppress UI beyond a minimal operator escape hatch (can be a follow-up).

## Decisions

**1. Branch point lives in the discovery consumer, reusing the admin usecase helpers.**
The consumer calls `resolveOrCreateVenue` → `detectDuplicateEvent`. `nil` → `buildAndInsertConcerts`
+ publish `CONCERT.created`; conflict → upsert `staged_concert` (today's staging path). This keeps
one canonical duplicate-detection implementation and avoids drift between discovery and approval.
*Alternative considered:* keep the branch at approval and add an "auto-approve" flag — rejected;
it still forces every concert through the queue table and a second processing hop.

**2. Venue row is created only on the auto-publish path.** A conflict resolves to the existing
event's venue, so `resolveOrCreateVenue` returns an existing row (no insert) whenever a conflict is
detected; a brand-new venue implies no existing event there, i.e. the new/publish path. This
preserves the "no orphan venues for never-published concerts" guarantee without extra bookkeeping.

**3. Origin is a column on the published event.** Add `origin` (enum: `auto_published` /
`admin_approved`) and `auto_published_at` (nullable `TIMESTAMPTZ`) to `events`. Approval sets
`admin_approved`; the consumer's auto-publish sets `auto_published` + `auto_published_at`. The admin
`List` response gains additive fields. The "recently auto-published" view is a client-side filter on
`origin = auto_published AND auto_published_at >= now - window`; the 7-day window is presentation-only
(no server state), so aging needs no background job. *Naming:* per backend schema-lint, avoid a bare
`created_at`; `auto_published_at` is domain-specific and allowed.

**4. Suppression is its own table, not the rejection log.** New `suppressed_concerts` keyed by the
**event** natural key `(venue_id, local_event_date, start_at)` with `NULLS NOT DISTINCT` on
`start_at` to mirror the `events` unique key exactly. `FilterNew` gains a third exclusion source
alongside published events and pending staged rows. `Delete` writes a suppression row inside the same
transaction as the cascade delete. The `rejected_concerts_log` stays analysis-only. *Alternative:*
reuse the rejection log with a "suppress" flag — rejected; the spec explicitly keeps that log
non-suppressing and analysis-only, and conflating the two invites accidental suppression.
*Un-suppress:* delete the `suppressed_concerts` row (minimal operator path; UI optional follow-up).

**5. Suppression key granularity matches the event-level deletion, and applies regardless of origin.**
`Delete` removes an entire event `(venue_id, local_event_date, start_at)` by cascade, independent of
performing artist, so the suppression key is the same triple — no `artist_id`. This prevents a
co-headliner's per-artist discovery from resurrecting a physical slot the operator deleted. Keying is
origin-agnostic: deleting a `admin_approved` concert must also suppress, because after auto-publish a
deleted-then-rediscovered concert would otherwise return as `auto_published` with no review. The
deleted event already carries `venue_id`/`local_event_date`/`start_at`, so the suppression row is
derived directly from it — no Google Places call at delete. *Alternative considered:* key by
`(artist_id, venue_id, local_event_date, start_at)` to match the per-artist discovery model — rejected
as weaker than the deletion granularity (a different performer could resurrect the slot).

## Risks / Trade-offs

- **Auto-publishing the least-anchored data** → New concerts have no existing counterpart to
  validate against, yet they now publish and notify without review. Mitigation: the recently-
  auto-published review view + one-click delete-with-suppression is the safety net; immediate
  notification is an accepted product decision.
- **Immediate push for a hallucinated concert cannot be recalled** → Accepted. Mitigation: keep the
  review window tight enough that operators catch bad rows soon; deleting suppresses re-creation.
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

1. Atlas migration: add `events.origin` (default `admin_approved` for existing rows) + nullable
   `events.auto_published_at`; create `suppressed_concerts`.
2. Backend: move the branch into the consumer; `Delete` writes suppression; `FilterNew` consults it.
   Ship behind the discovery consumer so behavior only changes on the next discovery run.
3. Proto (BSR): additive `origin` + `auto_published_at` on the admin `List` concert message.
4. Frontend admin console: recently-auto-published review view + delete action.
5. Rollback: revert the consumer branch to always-stage; the new columns/table are inert if unused.
