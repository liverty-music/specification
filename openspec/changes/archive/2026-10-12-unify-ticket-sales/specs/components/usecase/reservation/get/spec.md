# Spec Delta

## REMOVED Requirements

### Requirement: The fan's own checkout
**Reason**: ReservationUseCase is renamed CheckoutUseCase and works on a Checkout of a TicketType; the fan's full name and phone number are stored on the User.
**Migration**: The behavior continues in `components/usecase/checkout/get`; the data moves in this change's migration.
