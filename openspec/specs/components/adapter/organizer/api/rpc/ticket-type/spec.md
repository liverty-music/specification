# components/adapter/organizer/api/rpc/ticket-type Specification

## Purpose
The organizer-facing ticket type service boundary: how an operator's sign-in is turned into their own Organizer before a TicketType's price, quantity or per-account limit is changed.

## Requirements

### Requirement: Update acts for the caller's own active Organizer

Update SHALL pass the same organizer-console sign-in checks as the organizer Organizer service, and SHALL then resolve the caller's own Organizer through OrganizerUseCase.ResolveCaller with the caller's tenant. When the caller has no tenant, the call SHALL fail with PermissionDenied. A failure of ResolveCaller SHALL be returned unchanged and nothing else runs. Update SHALL then run TicketTypeUseCase.Update for the resolved Organizer and return its errors unchanged. That the TicketType's sale belongs to the caller's Organizer is a precondition of the usecase, not of the boundary.

#### Scenario: Operator raises the quantity
- **WHEN** an operator of an active Organizer calls Update for a TicketType of their sale with a quantity of 180
- **THEN** TicketTypeUseCase.Update runs for their Organizer and the updated TicketType is returned

#### Scenario: Deactivated Organizer
- **WHEN** the caller's Organizer is deactivated
- **THEN** Update fails with FailedPrecondition and nothing changes

### Requirement: Update names the ticket type and its values

Update SHALL fail with InvalidArgument, before any usecase runs, when no TicketType, price, quantity or per-account limit is given, or when one is malformed.

#### Scenario: Missing quantity
- **WHEN** an operator calls Update without a quantity
- **THEN** it fails with InvalidArgument and nothing changes
