# components/adapter/organizer/api/rpc/ticket-stock Specification

## Purpose
The organizer-facing ticket stock service boundary (`TicketStockService`): how a member's sign-in is turned into their own Organizer before an event's ticket stocks are created, deleted or listed.

## Requirements

### Requirement: Every call acts for the caller's own active Organizer

Create, Delete and ListByEvent SHALL pass the same organizer-console sign-in checks as the organizer Organizer service, and SHALL then resolve the caller's own Organizer through OrganizerUseCase.ResolveCaller with the caller's Organization. When the caller has no Organization, the call SHALL fail with PermissionDenied. A failure of ResolveCaller SHALL be returned unchanged and nothing else runs. Only then SHALL the boundary run, for the resolved Organizer, TicketStockUseCase.Create, Delete or ListByEvent; errors from the usecase SHALL be returned unchanged. That the event, seat type or stock belongs to the caller's Organizer is a precondition of the usecase, not of the boundary.

#### Scenario: Member stocks an event
- **WHEN** a member of an active Organizer calls Create for 150 S席 tickets of their event
- **THEN** TicketStockUseCase.Create runs for their Organizer and the TicketStock is returned

#### Scenario: Deactivated Organizer
- **WHEN** the caller's Organizer is deactivated
- **THEN** every call fails with FailedPrecondition and nothing changes

### Requirement: Calls name their values

Each call SHALL fail with InvalidArgument, before any usecase runs, when a value it needs is missing or malformed: Create, when no event, SeatType or quantity is given; Delete, when no TicketStock is given; ListByEvent, when no event is given.

#### Scenario: Missing quantity
- **WHEN** a member calls Create without a quantity
- **THEN** it fails with InvalidArgument and nothing is stored

#### Scenario: ListByEvent without an event
- **WHEN** ListByEvent is called without an event
- **THEN** it fails with InvalidArgument
