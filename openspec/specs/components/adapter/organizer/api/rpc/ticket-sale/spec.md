# components/adapter/organizer/api/rpc/ticket-sale Specification

## Purpose
The organizer-facing ticket sale service boundary: how a member's sign-in is turned into their own Organizer before a sale is configured or read.

## Requirements

### Requirement: Every call acts for the caller's own active Organizer

Create, ListByEvent, SetWindow and SetVerificationRequirement SHALL pass the same organizer-console sign-in checks as the organizer Organizer service, and SHALL then resolve the caller's own Organizer through OrganizerUseCase.ResolveCaller with the caller's Organization. When the caller has no Organization, the call SHALL fail with PermissionDenied. A failure of ResolveCaller SHALL be returned unchanged and nothing else runs: PermissionDenied when no Organizer is linked to the Organization or the Organizer is provisioning, and FailedPrecondition when it is deactivated. Only then SHALL the boundary run, for the resolved Organizer, TicketSaleUseCase.Create for Create, ListOwnByEvent for ListByEvent, SetWindow for SetWindow and SetVerificationRequirement for SetVerificationRequirement; errors from the usecase SHALL be returned unchanged. That the Series, event or sale belongs to the caller's Organizer is a precondition of the usecase, not of the boundary.

#### Scenario: Member configures a sale

- **WHEN** a member of an active Organizer calls Create for a FirstCome or Lottery sale on its published events
- **THEN** the sale is created and returned naming its events

#### Scenario: Member sees how many sold

- **WHEN** a member calls ListByEvent for their event
- **THEN** TicketSaleUseCase.ListOwnByEvent runs for their Organizer and the event's sales are returned with the entry stats of each TicketStock

#### Scenario: Member moves a window

- **WHEN** a member calls SetWindow for a sale on their Series
- **THEN** TicketSaleUseCase.SetWindow runs for their Organizer and the updated sale is returned

#### Scenario: Organization with no Organizer

- **WHEN** no Organizer is linked to the caller's Organization
- **THEN** the call fails with PermissionDenied and nothing is created

#### Scenario: Deactivated Organizer

- **WHEN** the caller's Organizer is deactivated
- **THEN** every call fails with FailedPrecondition

### Requirement: Calls name their events and values

Each call SHALL fail with InvalidArgument, before any usecase runs, when a value it needs is missing or malformed:
- Create, when no Series, name, method, start time, end time or event is given;
- ListByEvent, when no event is given;
- SetWindow, when no sale, start time or end time is given;
- SetVerificationRequirement, when no sale is given. A request that gives no requirement sets None.

#### Scenario: Sale without events

- **WHEN** Create is called with no event
- **THEN** it fails with InvalidArgument and nothing is created

#### Scenario: Create without an end time

- **WHEN** Create is called without an end time
- **THEN** it fails with InvalidArgument and nothing is created

#### Scenario: ListByEvent without an event

- **WHEN** ListByEvent is called without an event
- **THEN** it fails with InvalidArgument

#### Scenario: SetWindow without an end time

- **WHEN** SetWindow is called without an end time
- **THEN** it fails with InvalidArgument and nothing changes
