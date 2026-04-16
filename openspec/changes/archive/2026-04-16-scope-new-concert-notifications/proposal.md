## Why

When new concerts are persisted for an artist, followers currently receive notifications whose filtering and payload are computed from **all** upcoming concerts of that artist — not only the freshly created ones. This causes over-notification (e.g., a `hype=home` follower in JP-13 gets notified about a new JP-40 concert because an unrelated JP-13 concert already exists) and incorrect counts in the notification body. The root cause is that the `CONCERT.created` event carries only a count, forcing the consumer to re-fetch the full upcoming list and placing business logic inside the event handler.

Operationally, there is also no deterministic way to integration-test the delivery pipeline today: the only way to trigger it is to call `ConcertService.SearchNewConcerts` and hope Gemini discovers a new concert, which is non-deterministic.

## What Changes

- **BREAKING** Event payload for `CONCERT.created` changes shape: from `{artist_id, artist_name, concert_count}` to `{artist_id, concert_ids[]}`, carrying identifiers of **only the newly created concerts**. Pre-existing events in the NATS `CONCERT` stream (dev/staging) will be **purged** on deploy — no dual-compat shim.
- Notification delivery becomes **scoped to newly created concerts**: the `HOME` / `NEARBY` hype filter and the notification payload count are computed exclusively over the newly-created concert set.
- The consumer handler for `CONCERT.created` becomes a thin adapter: it parses the CloudEvent and delegates to the use case without any repository lookups. All domain logic (artist hydration, concert hydration by IDs, follower filtering, push dispatch) moves into the use case.
- New RPC `PushNotificationService.NotifyNewConcerts(artist_id, concert_ids[])` for deterministic integration testing and operator-initiated re-delivery. Invokes the same use case path, bypassing the NATS hop.
- The new RPC is **debug/admin-only**: it returns `PERMISSION_DENIED` in production (gated via the existing `ENVIRONMENT` config), so no new env var is introduced.

## Capabilities

### New Capabilities

_None — all changes extend the existing `push-notification-service` capability._

### Modified Capabilities

- `push-notification-service`:
  - New requirement: delivery is scoped to newly-created concerts only (filtering and payload both).
  - New requirement: `CONCERT.created` event carries `artist_id` + `concert_ids[]` and is not published when no concerts are created.
  - New requirement: consumer handler is a thin adapter (no direct repository access); business logic lives in the use case.
  - New requirement: `NotifyNewConcerts` debug RPC for deterministic integration testing, restricted to non-production environments.

## Impact

- **Protobuf (specification repo)**: new RPC method on `PushNotificationService`; new request/response messages. Breaking check needs no label (method addition is non-breaking at proto level).
- **Backend (Go)**:
  - `internal/entity/event_data.go`: remove `ConcertCreatedData` (moves to usecase layer).
  - `internal/usecase/`: introduce `usecase.ConcertCreatedData` struct, change `NotifyNewConcerts` signature, add internal hydration.
  - `internal/entity/concert.go` and `internal/infrastructure/database/rdb/concert_repo.go`: add `ConcertRepository.ListByIDs`.
  - `internal/usecase/concert_creation_uc.go`: publisher emits `concert_ids`; skip publish on empty.
  - `internal/adapter/event/notification_consumer.go`: slimmed; remove artist/concert repo deps.
  - `internal/adapter/rpc/push_notification_handler.go`: implement `NotifyNewConcerts` RPC.
  - `internal/di/`: remove artist/concert deps from notification consumer wiring; register the debug RPC handler unconditionally, with in-handler `cfg.IsProduction()` gate.
  - Tests across usecase/adapter layers updated to the new shape.
- **Operations**: NATS `CONCERT` stream purge required on dev/staging deploy (single-time operation).
- **Downstream frontend**: unaffected (no client-facing RPC behavior change; `NotifyNewConcerts` is operator-facing).
