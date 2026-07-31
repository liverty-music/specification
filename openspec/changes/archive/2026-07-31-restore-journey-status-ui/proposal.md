## Why

Commit `0245f03` removed the journey status badge from the event card and the journey selection section from the event detail sheet under the assumption that the entire ticket feature was not service-ready. However, journey status (user self-reporting of ticket acquisition state: tracking → applied → paid/lost) is functionally independent of ticket sales — the backend `TicketJourneyService` is already deployed and operational. The removal broke a working user-facing feature.

## What Changes

- **Restore** the journey badge in the event card (`event-card.html`), showing the user's current journey status as an emoji icon in the card's corner.
- **Restore** the journey selection section in the event detail sheet (`event-detail-sheet.html`), allowing authenticated users to set/update/remove their ticket acquisition status for a concert.
- The Tickets bottom-nav tab (ZK proof entry feature) remains hidden — it is a separate, unrelated feature.

## Capabilities

### New Capabilities

None. This change restores previously removed UI backed by existing, already-shipped capabilities.

### Modified Capabilities

- `ticket-journey`: The UI requirements for `Ticket Status UI visibility` and the full journey selection control (two-phase layout, cumulative progress, radiogroup accessibility) were effectively un-rendered by the deletion. Restoring the HTML makes these requirements active again — no spec text changes are needed, the existing requirements are simply being satisfied again.
- `journey-status-presentation`: The `Consistent rendering across components` requirement specifies that the concert-card badge must be present. Restoring the badge makes this requirement satisfied again.

## Impact

- **Frontend only** — no backend, proto, or BSR changes required.
- Changed files: `src/components/live-highway/event-card.html`, `src/components/live-highway/event-detail-sheet.html`
- All ViewModel logic (`EventDetailSheet`, `EventCard`), CSS, `TicketJourneyStore`, and backend RPC are already intact.
- Unit tests for `EventDetailSheet` and `EventCard` already cover journey behavior and continue to pass without modification.
