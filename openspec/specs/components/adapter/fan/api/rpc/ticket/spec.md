# Ticket RPC

## Purpose

The fan-facing ticket service boundary: a fan reads only their own orders and tickets, and the buyer is always the caller.

## Requirements

### Requirement: The buyer is the signed-in caller

GetOrder and GetMyTickets SHALL require a signed-in caller and fail with Unauthenticated otherwise. They SHALL resolve the caller to their stored User (User.GetByExternalID) and pass that User to TicketUseCase.GetOrder and TicketUseCase.GetMyTickets; the request never names a buyer. When the caller has no stored account, the call SHALL fail with NotFound. GetOrder SHALL fail with InvalidArgument when no order is given.

Known defect: liverty-music/backend#471

#### Scenario: Fan lists their tickets

- **WHEN** a signed-in fan calls GetMyTickets
- **THEN** the tickets that fan holds are returned

#### Scenario: Not signed in

- **WHEN** a caller who is not signed in calls GetOrder
- **THEN** the call fails with Unauthenticated

#### Scenario: Missing order

- **WHEN** GetOrder is called without an order
- **THEN** it fails with InvalidArgument
