# Spec Delta

## REMOVED Requirements

### Requirement: Lapsed holds and leftover card holds handled within one minute
**Reason**: ReservationUseCase is renamed CheckoutUseCase and works on a Checkout of a TicketType; the fan's full name and phone number are stored on the User.
**Migration**: The behavior continues in `components/usecase/checkout/release-expired`; the data moves in this change's migration.

### Requirement: A charged hold on an ended checkout is reported
**Reason**: ReservationUseCase is renamed CheckoutUseCase and works on a Checkout of a TicketType; the fan's full name and phone number are stored on the User.
**Migration**: The behavior continues in `components/usecase/checkout/release-expired`; the data moves in this change's migration.
