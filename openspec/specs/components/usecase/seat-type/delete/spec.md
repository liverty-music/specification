# components/usecase/seat-type/delete Specification

## Purpose
SeatTypeUseCase.Delete lets an Organizer remove a seat type it created by mistake, as long as no event stocks tickets of it; a seat type's name and price never change, so a mistake is fixed by deleting and creating again.

## Requirements

### Requirement: Only a member of the owning Organizer deletes an unused seat type

Delete SHALL take the caller's Organizer and a SeatType. It SHALL read the SeatType with SeatType.Get and its Series with Series.GetAuthored, and fail with PermissionDenied, without revealing whether it exists, when the SeatType does not exist or its Series is owned by another Organizer. It SHALL then delete it with SeatType.Delete, which fails with FailedPrecondition when a TicketStock uses the SeatType; its failures are returned unchanged.

#### Scenario: Mistaken seat type
- **WHEN** a member deletes a SeatType that no TicketStock uses
- **THEN** it is deleted

#### Scenario: Seat type in stock
- **WHEN** a member deletes a SeatType that an event's TicketStock uses
- **THEN** Delete fails with FailedPrecondition and nothing changes

#### Scenario: Another Organizer's seat type
- **WHEN** a member deletes a SeatType of a Series owned by another Organizer
- **THEN** Delete fails with PermissionDenied and nothing changes
