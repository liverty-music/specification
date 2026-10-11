# components/adapter/organizer/api/rpc/ticket-sale Specification

## Purpose
The organizer-facing ticket sale service boundary: how an operator's sign-in is turned into their own Organizer before a sale is configured or read.

## Requirements

### Requirement: Every call acts for the caller's own active Organizer

Configure and Get SHALL pass the same organizer-console sign-in checks as the organizer Organizer service, and SHALL then resolve the caller's own Organizer through OrganizerUseCase.ResolveCaller with the caller's tenant. A failure of ResolveCaller SHALL be returned unchanged and nothing else runs. Configure SHALL run TicketSaleUseCase.Configure, and Get SHALL run TicketSaleUseCase.GetOwn, for the resolved Organizer; errors from the usecase SHALL be returned unchanged.

#### Scenario: Operator configures a sale

- **WHEN** an operator of an active Organizer calls Configure for their published event
- **THEN** the sale is configured and returned

#### Scenario: Operator sees how many sold

- **WHEN** an operator calls Get for their event's sale
- **THEN** TicketSaleUseCase.GetOwn runs for their Organizer and the sale is returned with its counts

#### Scenario: Deactivated Organizer

- **WHEN** the caller's Organizer is deactivated
- **THEN** every call fails with FailedPrecondition

### Requirement: Calls name their event and values

Configure and Get SHALL fail with InvalidArgument, before any usecase runs, when the event is missing or malformed. Configure SHALL also fail with InvalidArgument when the sale start, the price or the quantity is missing.

#### Scenario: Missing price

- **WHEN** an operator calls Configure without a price
- **THEN** it fails with InvalidArgument and nothing is stored
