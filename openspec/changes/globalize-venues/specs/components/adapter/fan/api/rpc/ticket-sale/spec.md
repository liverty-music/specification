## MODIFIED Requirements

### Requirement: A returned sale shows states, never counts

A TicketSale returned by the fan boundary SHALL carry its id, Series, name, method, start time, end time and verification requirement, with the start and end time each given as the local date-time in the sale's time zone together with that time zone. Each TicketStock returned with the event's sales SHALL carry its id, event, SeatType name and price, its state, whether it is LowStock, and whether its resale is open, and the event's per-account limit SHALL be returned beside them. It SHALL NOT carry a TicketStock's quantity, sold count, or held count, nor the stocks of a sale's other events, so no fan learns how many tickets remain.

#### Scenario: Few left without a count

- **WHEN** ListByEvent returns a TicketStock of 150 that is Available and LowStock with 15 remaining
- **THEN** the response carries its state, LowStock, seat type and price, and no quantity, sold count or held count

#### Scenario: Sold out

- **WHEN** ListByEvent returns a TicketStock that sold out before its resale deadline
- **THEN** the response says it is SoldOut and its resale is open, and carries no count

#### Scenario: Sale window in its own time zone

- **WHEN** ListByEvent returns a sale in Asia/Taipei that runs from 2026-11-01 12:00 to 2026-11-07 23:59
- **THEN** the response carries the start 2026-11-01 12:00 and the end 2026-11-07 23:59, each with the time zone Asia/Taipei
