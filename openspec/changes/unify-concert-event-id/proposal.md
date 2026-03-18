## Why

The proto `Concert` message uses `ConcertId` as its identifier, but the underlying Go entity and database both use `event_id` (the `events` table). Meanwhile, the ticket/entry domain already uses `EventId` for the same underlying UUID. This naming split creates cognitive overhead for developers and risks cross-domain bugs where someone assumes `ConcertId` and `EventId` are different identifiers.

Fixing this now is cheap — `ConcertId` is only referenced in 3 places within `concert.proto`. The longer we wait, the more downstream consumers will depend on the `ConcertId` type.

## What Changes

- **BREAKING**: Remove the `ConcertId` message from `concert.proto`.
- **BREAKING**: Change `Concert.id` field type from `ConcertId` to `EventId`.
- Move the `EventId` message definition from `ticket.proto` to `event.proto`, where it belongs as a first-class entity identifier alongside `Event`.
- Update `ticket.proto` to import `EventId` from its new location.
- Update all RPC request/response messages that reference `ConcertId` (currently none outside `concert.proto`).

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `concert-service`: The `Concert` entity's identifier type changes from `ConcertId` to `EventId`, aligning the proto schema with the database and Go domain model.
- `event-management`: `EventId` is relocated from `ticket.proto` to `event.proto` as the canonical event identifier.

## Impact

- **Proto (specification)**: `concert.proto`, `event.proto`, `ticket.proto` modified. Breaking change requires a semver major or minor bump with breaking label.
- **Backend (Go)**: RPC mapper must map `Concert.ID` ↔ `EventId` instead of `ConcertId`. `ConcertId` type removed from generated code.
- **Frontend (TypeScript)**: Any references to `ConcertId` type in generated client code must switch to `EventId`.
- **BSR consumers**: All downstream packages regenerated after release. Draft PRs for backend/frontend can be prepared in advance.
