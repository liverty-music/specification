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
publish automatically while conflicts keep the human reconciliation gate, and adds
a lightweight post-hoc safety net so an operator can retract a bad auto-published
concert.

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
- **Origin marking.** Published events record whether they were auto-published or
  approved by a developer, and when they were auto-published, so a review view can
  surface recently auto-published concerts.
- **Post-hoc moderation with suppression.** Deleting an auto-published concert
  records a suppression entry keyed by the concert's natural key; re-discovery
  SHALL NOT auto-publish or re-stage a suppressed natural key. This breaks the
  "delete → Gemini re-discovers → auto-publishes again" loop. Suppression is a new
  concept, distinct from the analysis-only `rejected_concerts_log` (which remains
  non-suppressing).
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
- `admin-concert-management`: published concerts carry an origin (auto-published
  vs developer-approved) and auto-publish timestamp exposed on the admin `List`
  surface so the console can present a recently-auto-published review view;
  `Delete` of an auto-published concert additionally records a suppression entry.

## Impact

- **Backend (Go):**
  - `internal/adapter/event/concert_consumer.go` + `internal/usecase/concert_creation_uc.go`: move venue get-or-create + `detectDuplicateEvent` into the discovery consumer; branch auto-publish vs stage.
  - `internal/usecase/concert_admin_uc.go`: `Approve` becomes reconciliation-only; `Delete` records suppression.
  - Discovery `FilterNew` dedup (`internal/usecase/concert_uc.go`) additionally consults the suppression set.
  - DB migration (Atlas): `events` gains an origin + auto-published-at column; a new suppression table keyed by concert natural key.
- **Proto/BSR:** admin `ConcertService.List` response gains origin + auto-published-at fields (additive). No breaking proto change expected.
- **Frontend (admin console):** new "recently auto-published" review view (time-based aging, default 7-day window) with a delete action wired to the existing `Delete` RPC.
- **Notifications:** auto-published new concerts emit `CONCERT.created` immediately, so followers are notified without a review step. A push whose concert is later deleted may deep-link to a removed event; the concert-detail deep-link path should degrade gracefully.
