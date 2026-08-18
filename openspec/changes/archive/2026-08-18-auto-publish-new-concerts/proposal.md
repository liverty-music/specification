## Why

Every concert the search pipeline discovers is currently staged as `pending` and
requires a developer to approve it one by one — including brand-new concerts that
have no existing counterpart to reconcile against. In practice the vast majority
of the queue is brand-new concerts, so approval is mostly rubber-stamping. Now
that Gemini search quality has improved, the manual gate on brand-new concerts
buys little and costs a lot of reviewer time.

The remaining hard cases are the *conflicts*: a discovered concert that collides
with an already-published event at the same `(venue, date, start)` and where a
human must decide which record to keep. Those still need judgment.

This change moves the new-vs-conflict decision earlier so that new concerts
publish automatically while conflicts keep the human reconciliation gate. The
post-hoc safety net reuses what already exists: an operator retracts a bad concert
through the existing admin `Delete`, and a new suppression concept makes that
deletion durable by stopping re-discovery from re-publishing the same slot. No new
review surface is introduced — the existing full-catalog admin `List` is the
retraction entry point.

## What Changes

- **Auto-publish brand-new concerts.** The `CONCERT.discovered` consumer resolves
  the venue and runs duplicate detection up front. When the discovered concert is
  genuinely new (no existing event at the resolved `(venue_id, local_date,
  start_at)`), it publishes the concert directly — inserting the
  `series`/`events`/`event_performers` rows and emitting `CONCERT.created` (so
  follower push notifications fire immediately) — instead of writing a `pending`
  staged row.
- **Conflicts still go to the queue.** When duplicate detection finds a collision,
  the concert is staged as `pending` exactly as today, and the developer resolves
  it via the existing `Approve` reconciliation (`KeepExisting` / `AdoptStaged`).
  The conflict definition is unchanged (same-slot collision at the resolved
  `(venue_id, local_date, start_at)`; the known-start "fill" case is not a
  conflict).
- **Post-hoc moderation with suppression.** Deleting a published concert (via the
  existing admin `Delete`) records a suppression entry keyed by the concert's
  natural key; re-discovery SHALL NOT auto-publish or re-stage a suppressed natural
  key. This breaks the "delete → Gemini re-discovers → auto-publishes again" loop.
  Suppression is a new concept, distinct from the analysis-only
  `rejected_concerts_log` (which remains non-suppressing). No provenance tracking
  (origin / auto-publish timestamp) and no dedicated review view are added — see the
  Non-Goals in design.md.
- **BREAKING (operational, not API):** the approval queue's meaning narrows —
  `pending` staged rows now represent only conflicts, not all discovered concerts.

## Capabilities

### New Capabilities
<!-- none -->

### Modified Capabilities
- `concert-approval-queue`: discovery no longer stages every concert — new
  concerts are auto-published, only conflicts are staged; the `Approve` path is
  now reconciliation-only; re-discovery dedup additionally consults a suppression
  set; a new suppression requirement covers deletion of auto-published concerts.
- `admin-concert-management`: `Delete` of a published concert additionally records
  a suppression entry (keyed by the deleted event's natural key) so a later
  discovery run does not re-create it. `List` is unchanged.

## Impact

- **Backend (Go):**
  - `internal/adapter/event/concert_consumer.go` + `internal/usecase/concert_creation_uc.go`: move venue get-or-create + `detectDuplicateEvent` into the discovery consumer; branch auto-publish vs stage.
  - `internal/usecase/concert_admin_uc.go`: `Approve` becomes reconciliation-only; `Delete` records suppression.
  - Discovery `FilterNew` dedup (`internal/usecase/concert_uc.go`) additionally consults the suppression set.
  - DB migration (Atlas): a single new suppression table keyed by concert natural key. The `events` table is unchanged (no new columns, no backfill).
- **Proto/BSR:** none. The admin `List` and `Delete` RPCs are reused as-is; no schema change, no BSR release coordination.
- **Frontend (admin console):** none. Retraction uses the existing full-catalog `List` + `Delete`; no new review view.
- **Notifications:** auto-published new concerts emit `CONCERT.created` immediately, so followers are notified without a review step. A push whose concert is later deleted may deep-link to a removed event; the concert-detail deep-link path already degrades gracefully (existing deeplink-push handling).
