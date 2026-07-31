## ADDED Requirements

### Requirement: Ticket Journey UI is independent of ticket sales
The Ticket Journey status UI (concert-card badge and detail-sheet status control) SHALL be available to authenticated users independently of any ticket purchase, NFT minting, ZK proof generation, or ticket sales navigation features. Hiding or removing those sales-side features SHALL NOT affect the availability of the Ticket Journey UI.

#### Scenario: Journey UI visible when ticket sales nav is hidden
- **WHEN** the Tickets bottom-nav tab is hidden (ticket sales feature not yet service-ready)
- **THEN** the journey status badge SHALL still appear on event cards for users who have a journey status
- **AND** the journey selection control SHALL still appear in the event detail sheet for authenticated users

#### Scenario: Journey UI does not depend on ticket purchase flow
- **WHEN** a user has not completed any ticket purchase or NFT minting
- **THEN** the user SHALL still be able to set and view their journey status (e.g. `tracking`, `applied`, `lost`, `unpaid`, `paid`) via the UI
