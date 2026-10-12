# Ticket RPC

## Purpose

The fan-facing ticket service boundary: a fan reads only their own orders and tickets, and the Order's user is always the caller.

## Requirements

### Requirement: The ticket's user is the signed-in caller

List SHALL require a signed-in caller and fail with Unauthenticated otherwise. It SHALL resolve the caller to their stored User (User.GetByProviderUserID) and pass that User to TicketUseCase.List; the request never names a user. When the caller has no stored account, the call SHALL fail with NotFound.

#### Scenario: Fan lists their tickets

- **WHEN** a signed-in fan calls List
- **THEN** the tickets that fan holds are returned

#### Scenario: Not signed in lists tickets

- **WHEN** a caller who is not signed in calls List
- **THEN** the call fails with Unauthenticated
