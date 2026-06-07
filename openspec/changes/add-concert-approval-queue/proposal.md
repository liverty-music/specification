## Why

Concerts are discovered by a Gemini-grounded searcher and **persisted automatically** the moment `CONCERT.discovered` fires. While the searcher's precision is still stabilizing, this means hallucinated or mis-extracted events (wrong date, wrong venue, non-existent show) reach fans immediately — and the only remedy today is a manual DB delete, which the **daily discovery cron re-creates the next day** because the deterministic series id and the dedup rule both regenerate the exact same row. There is no human checkpoint and no way to stop a known-bad event from re-appearing.

This change inserts a **developer approval gate** between discovery and publication. Discovered concerts land in a staging queue; a developer reviews each one in the admin console and **approves** (publish to fans) or **rejects** (drop). Reject is intentionally **non-permanent** — the next discovery run may bring corrected data and re-surface the item for re-review — but every rejection is recorded in an append-only log so we can study which errors the searcher repeats and feed that back into searcher tuning. This is a **temporary quality measure**: once searcher precision stabilizes, the gate can be relaxed (e.g. an auto-approve allowlist) without re-architecting.

This is the admin console's first business feature, building on the access-controlled shell delivered by the `admin-console` capability.

## What Changes

- **Route discovery through a staging queue instead of direct insert.** The `CONCERT.discovered` consumer no longer writes to `events`. It resolves the venue (Google Places) up front so the reviewer sees the canonical venue, then writes a `staged_concert` row in `pending` state. `events`/`series`/`event_performers`/`venues` are written only on **approval**.
- **Move `CONCERT.created` to approval time.** The downstream pipeline (push notifications "new concert!") fires when a developer approves, never on raw discovery — so fans are never notified about unverified data.
- **Add an admin-only moderation service.** New admin-scoped RPCs: list pending concerts (with resolved-venue preview), approve, reject (with reason). Authorized only for the admin org, consistent with the admin console's auth boundary.
- **Build the approval-queue UI in the admin console.** A reviewer screen listing pending concerts with all reviewable fields (artist, title, date, start time, raw listed venue name, resolved venue name + admin_area, source URL, discovered-at) and approve/reject actions.
- **Extend dedup so re-discovery respects the queue.** A discovered concert is skipped only when its natural key already exists in `events` (published) **or** as a `pending` staged row. Rejected items are **not** suppressed — they may re-enter the queue on a later run.
- **Record every rejection in an append-only `rejected_concerts_log`** (raw payload, resolved venue, reason, timestamp, reviewer). Used for searcher-quality analysis only; it never suppresses future discovery.

## Capabilities

### New Capabilities
- `concert-approval-queue`: The staging lifecycle (`pending` → approved/published or rejected/dropped) for Gemini-discovered concerts, the up-front venue resolution at staging time, the re-discovery dedup rule that consults published + pending (but not rejected) state, the append-only rejection log, the admin-scoped moderation RPCs, and the admin-console reviewer UI.

### Modified Capabilities
- `concert-service`: The **Concert Persistence** requirement changes from "automatically persist any new concert discovered" to "stage any new concert discovered for approval; persist only on approval." The **Search Concerts by Artist** dedup scenario is extended so newly discovered concerts also exclude those already sitting in the approval queue as `pending`.

## Impact

- **specification**: New `rpc/admin/v1/concert_moderation_service.proto` (`ConcertModerationService` with `ListPendingConcerts`, `ApproveConcert`, `RejectConcert`, and a `PendingConcert` message carrying the staged data plus resolved-venue preview). No change to `entity/v1/concert.proto` or `entity/v1/event.proto` — the published entity shape is unchanged.
- **backend**: Atlas migration for `staged_concerts` and `rejected_concerts_log`. New `StagedConcert` entity + `StagedConcertRepository`. The `CONCERT.discovered` consumer (`CreateFromDiscovered`) is split: venue-resolve + stage on discovery; the existing series/event/performer insert path moves behind a new "approve" use case that also publishes `CONCERT.created`. `FilterNew` dedup extended to consult `staged_concerts(pending)`. New admin RPC handler with admin-org authorization (per `rpc-auth-scoping`).
- **frontend**: New approval-queue route + components in the `admin/` app (bundle-isolated from the consumer SPA), consuming `ConcertModerationService`.
- **cloud-provisioning**: None expected — no new job or manifest; the existing discovery cron is unchanged (it still calls `SearchNewConcerts`; only the downstream consumer behavior changes).
- **Product tradeoff (accepted)**: Onboarding loses concert immediacy for **brand-new artists nobody has followed before** — their concerts stay invisible until a developer approves. Already-followed (popular) artists are largely pre-approved via the daily cron, so the common onboarding path is mostly unaffected. Accepted as a temporary cost of the quality gate.
- **Out of scope**: event-level delete of already-approved concerts (post-publication correction — a separate change); the admin venue-list / duplicate-detection screen (separate change `add-admin-venue-list`); auto-approve allowlist / confidence-based auto-approval (a later relaxation once precision stabilizes).
