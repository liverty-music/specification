# Spec Delta

## REMOVED Requirements

### Requirement: The reservation's order
**Reason**: An Order's source is a Checkout instead of a Reservation; GetByReservationID is renamed GetByCheckoutID.
**Migration**: The behavior continues in `components/entity/order/get-by-checkout-id`; the data moves in this change's migration.
