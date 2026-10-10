# Spec Delta

## Purpose

The organizer-facing ticket sale service boundary: how an operator's sign-in is turned into their own Organizer before a TicketSale is created, listed or changed.

## ADDED Requirements

### Requirement: Every ticket sale call acts for the caller's own active Organizer

Create, List and SetVerificationRequirement SHALL pass the same organizer-console sign-in checks as the organizer Organizer service, and SHALL then resolve the caller's own Organizer through OrganizerUseCase.ResolveCaller with the caller's tenant. When the caller has no tenant, the call SHALL fail with PermissionDenied. A failure of ResolveCaller SHALL be returned unchanged: PermissionDenied when no Organizer is linked to the tenant or the Organizer is provisioning, and FailedPrecondition when it is deactivated. Only then SHALL the boundary call TicketSaleUseCase.Create, ListOwnByEvent or SetVerificationRequirement. That the Series, event or sale belongs to the caller's Organizer is a precondition of the usecase, not of the boundary.

#### Scenario: Active Organizer creates a sale
- **WHEN** an operator of an active Organizer creates a lottery sale for its published events
- **THEN** the sale is created and returned

#### Scenario: Tenant with no Organizer
- **WHEN** no Organizer is linked to the caller's tenant
- **THEN** the call fails with PermissionDenied and nothing is created

#### Scenario: Deactivated Organizer
- **WHEN** the caller's Organizer is deactivated
- **THEN** the call fails with FailedPrecondition

### Requirement: Ticket sale requests are validated at the boundary

Create SHALL fail with InvalidArgument, before any usecase runs, when no Series, name, method, start time, end time or TicketType is given, or when a TicketType has no event, price or quantity. List SHALL fail with InvalidArgument when no event is given. SetVerificationRequirement SHALL fail with InvalidArgument when no sale or requirement is given.

#### Scenario: Sale without ticket types
- **WHEN** Create is called with no TicketType
- **THEN** it fails with InvalidArgument and nothing is created

#### Scenario: List without an event
- **WHEN** List is called without an event
- **THEN** it fails with InvalidArgument
