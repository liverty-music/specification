## ADDED Requirements

### Requirement: A created discovered sale is announced with its creation

When UpsertDiscovered creates a discovered sale (Inserted), it SHALL announce the TicketSale as discovered, together with the creation: both are stored or neither is. A sale it updates (Updated) or skips (Skipped) SHALL NOT be announced. When the announcement cannot be recorded, UpsertDiscovered SHALL fail with Unavailable and store nothing.

#### Scenario: New sale

- **WHEN** UpsertDiscovered creates a discovered lottery and returns Inserted
- **THEN** one discovered sale is announced, carrying that TicketSale

#### Scenario: Known sale discovered again

- **WHEN** UpsertDiscovered updates a known discovered sale and returns Updated
- **THEN** nothing is announced

#### Scenario: Announcement cannot be recorded

- **WHEN** UpsertDiscovered would create a discovered sale and the announcement cannot be recorded
- **THEN** UpsertDiscovered fails with Unavailable and no sale is stored
