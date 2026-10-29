# components/entity/seat-type/delete Specification

## Purpose
Removes a SeatType that no TicketStock uses, so a mistaken name or price is fixed by creating it again.

## Requirements

### Requirement: Delete an unused seat type

Delete SHALL remove the SeatType with the given id. It SHALL fail with FailedPrecondition, removing nothing, when a TicketStock uses the SeatType, also one created while Delete runs, and with NotFound when no SeatType has the id.

#### Scenario: Unused seat type
- **WHEN** Delete is called for a SeatType no TicketStock uses
- **THEN** the SeatType is removed

#### Scenario: Stocked seat type
- **WHEN** an event of the Series has a TicketStock of the SeatType
- **THEN** Delete fails with FailedPrecondition and the SeatType remains

#### Scenario: Unknown id
- **WHEN** no SeatType has the id
- **THEN** Delete fails with NotFound
