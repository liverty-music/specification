# Spec Delta

## REMOVED Requirements

### Requirement: Checkout calls are for the signed-in fan
**Reason**: ReservationService is replaced by CheckoutService, whose Start takes a TicketType and whose Authorize takes the fan's full name and phone number.
**Migration**: The behavior continues in `components/adapter/fan/api/rpc/checkout`; the data moves in this change's migration.

### Requirement: Requests are validated before any usecase runs
**Reason**: ReservationService is replaced by CheckoutService, whose Start takes a TicketType and whose Authorize takes the fan's full name and phone number.
**Migration**: The behavior continues in `components/adapter/fan/api/rpc/checkout`; the data moves in this change's migration.
