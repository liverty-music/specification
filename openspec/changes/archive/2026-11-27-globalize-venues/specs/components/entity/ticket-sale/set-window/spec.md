## MODIFIED Requirements

### Requirement: Set the window

SetWindow SHALL store the given start and end times, each a local date-time, and the given time zone in which both are read, for the TicketSale, leave its other attributes and its events unchanged and return the updated sale with its events. It SHALL fail with InvalidArgument when the window or the time zone breaks the TicketSale rules, and with NotFound when no TicketSale has the id.

#### Scenario: Window moved
- **WHEN** a sale running from 1 to 10 November is set to run from 2 to 11 November
- **THEN** the returned sale runs from 2 to 11 November and its events are unchanged

#### Scenario: Time zone changed with the window
- **WHEN** a sale running from 2026-11-01 12:00 to 2026-11-07 23:59 in Asia/Tokyo is set to run from 2026-11-01 12:00 to 2026-11-07 23:59 in Asia/Seoul
- **THEN** the returned sale has the time zone Asia/Seoul and the same local start and end, and its name, method, verification requirement and events are unchanged

#### Scenario: Lottery window too long
- **WHEN** a Lottery sale's window is set to 15 days
- **THEN** SetWindow fails with InvalidArgument and nothing changes

#### Scenario: Unknown time zone
- **WHEN** a sale's window is set with the time zone JST
- **THEN** SetWindow fails with InvalidArgument and nothing changes

#### Scenario: Unknown sale
- **WHEN** no TicketSale has the id
- **THEN** SetWindow fails with NotFound
