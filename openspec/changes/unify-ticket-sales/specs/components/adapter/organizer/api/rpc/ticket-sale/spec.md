# Spec Delta

## MODIFIED Requirements

### Requirement: Every call acts for the caller's own active Organizer

Create, ListByEvent, SetWindow and SetVerificationRequirement SHALL pass the same organizer-console sign-in checks as the organizer Organizer service, and SHALL then resolve the caller's own Organizer through OrganizerUseCase.ResolveCaller with the caller's tenant. When the caller has no tenant, the call SHALL fail with PermissionDenied. A failure of ResolveCaller SHALL be returned unchanged and nothing else runs: PermissionDenied when no Organizer is linked to the tenant or the Organizer is provisioning, and FailedPrecondition when it is deactivated. Only then SHALL the boundary run, for the resolved Organizer, TicketSaleUseCase.Create for Create, ListOwnByEvent for ListByEvent, SetWindow for SetWindow and SetVerificationRequirement for SetVerificationRequirement; errors from the usecase SHALL be returned unchanged. That the Series, event or sale belongs to the caller's Organizer is a precondition of the usecase, not of the boundary.

#### Scenario: Operator configures a sale

- **WHEN** an operator of an active Organizer calls Create for a FirstCome or Lottery sale on its published events
- **THEN** the sale is created and returned with its TicketTypes

#### Scenario: Operator sees how many sold

- **WHEN** an operator calls ListByEvent for their event
- **THEN** TicketSaleUseCase.ListOwnByEvent runs for their Organizer and the event's sales are returned with their counts

#### Scenario: Operator moves a window

- **WHEN** an operator calls SetWindow for a sale on their Series
- **THEN** TicketSaleUseCase.SetWindow runs for their Organizer and the updated sale is returned

#### Scenario: Tenant with no Organizer

- **WHEN** no Organizer is linked to the caller's tenant
- **THEN** the call fails with PermissionDenied and nothing is created

#### Scenario: Deactivated Organizer

- **WHEN** the caller's Organizer is deactivated
- **THEN** every call fails with FailedPrecondition

### Requirement: Calls name their event and values

Each call SHALL fail with InvalidArgument, before any usecase runs, when a value it needs is missing or malformed:
- Create, when no Series, name, method, start time or TicketType is given, or when a TicketType has no event, price or quantity; the end time and the per-account limit may be left out;
- ListByEvent, when no event is given;
- SetWindow, when no sale, start time or end time is given;
- SetVerificationRequirement, when no sale or requirement is given.

#### Scenario: Missing price

- **WHEN** an operator calls Create with a TicketType without a price
- **THEN** it fails with InvalidArgument and nothing is stored

#### Scenario: Sale without ticket types

- **WHEN** Create is called with no TicketType
- **THEN** it fails with InvalidArgument and nothing is created

#### Scenario: ListByEvent without an event

- **WHEN** ListByEvent is called without an event
- **THEN** it fails with InvalidArgument

#### Scenario: SetWindow without an end time

- **WHEN** SetWindow is called without an end time
- **THEN** it fails with InvalidArgument and nothing changes
