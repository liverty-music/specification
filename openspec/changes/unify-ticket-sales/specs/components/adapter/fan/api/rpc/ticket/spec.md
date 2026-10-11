# Spec Delta

## ADDED Requirements

### Requirement: The ticket's user is the signed-in caller

List SHALL require a signed-in caller and fail with Unauthenticated otherwise. It SHALL resolve the caller to their stored User (User.GetByExternalID) and pass that User to TicketUseCase.GetMyTickets; the request never names a user. When the caller has no stored account, the call SHALL fail with NotFound.

#### Scenario: Fan lists their tickets

- **WHEN** a signed-in fan calls List
- **THEN** the tickets that fan holds are returned

#### Scenario: Not signed in lists tickets

- **WHEN** a caller who is not signed in calls List
- **THEN** the call fails with Unauthenticated

## REMOVED Requirements

### Requirement: The buyer is the signed-in caller
**Reason**: A read of an Order belongs to OrderService under the RPC naming rule, so `TicketService.GetOrder` becomes `OrderService.Get(order_id)`; TicketService keeps List.
**Migration**: The List rule continues in "The ticket's user is the signed-in caller" above; the GetOrder rule, with the scenarios "Not signed in" and "Missing order", continues in `components/adapter/fan/api/rpc/order`.
