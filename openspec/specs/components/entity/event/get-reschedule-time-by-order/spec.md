# Event.GetRescheduleTimeByOrder

## Purpose

Returns when the Event that an Order's Tickets admit to was postponed, the anchor of the 延期 (postponement) refund window.

## Requirements

### Requirement: Reschedule time of the order's event

GetRescheduleTimeByOrder SHALL return the reschedule time of the Event that the Order's Tickets admit to, and no time when that Event has never been postponed. It SHALL fail with NotFound when the Order has no Ticket.

#### Scenario: Postponed event

- **WHEN** the Order's Tickets admit to an Event postponed on 2026-10-01
- **THEN** it returns 2026-10-01

#### Scenario: Never postponed

- **WHEN** the Order's Event has no reschedule time
- **THEN** it returns no time and no error

#### Scenario: Order without tickets

- **WHEN** the Order has no Ticket
- **THEN** it fails with NotFound
