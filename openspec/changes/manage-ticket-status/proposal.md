## Why

The platform currently auto-collects concert information and sends push notifications, but users have no way to track their personal ticket acquisition progress for each concert. In Japan's live music market, the ticket purchase process involves multiple stages (waiting for sales info, applying for lotteries, awaiting payment, completing payment) that users must manage manually across scattered tools. Adding per-event ticket journey tracking directly to the dashboard delivers the next step of the core product value: freeing users from the complexity of ticket management.

## What Changes

- Introduce a new `TicketJourney` entity representing a user's personal ticket acquisition status for a specific event.
- Add a `TicketJourneyStatus` enum with five states: `TRACKING`, `APPLIED`, `LOST`, `UNPAID`, `PAID`.
- Add a new `TicketJourneyService` RPC with `SetStatus`, `Delete`, and `ListByUser` operations.
- Add a `ticket_journeys` database table with composite PK `(user_id, event_id)`.
- Display ticket journey status as a badge on dashboard concert cards.
- Add status change UI to the event detail sheet.

## Capabilities

### New Capabilities
- `ticket-journey`: Per-event ticket acquisition tracking with status management, RPC service, and dashboard UI integration.

### Modified Capabilities
- `concert-detail`: Add ticket journey status display and change controls to the event detail sheet.
- `live-events`: Add ticket journey status badge overlay to dashboard concert cards.

## Impact

- **specification**: New entity proto (`ticket_journey.proto`), new RPC service proto (`ticket_journey_service.proto`).
- **backend**: New DB migration (`ticket_journeys` table), new entity/usecase/repository/handler layers for TicketJourney.
- **frontend**: Extended `Concert` entity with optional journey status, new API client for `TicketJourneyService`, UI changes to `event-card` and `event-detail-sheet` components.
- **BSR**: New generated Go and TypeScript packages for `ticket_journey` entity and service.
