# Spec Delta

## REMOVED Requirements

### Requirement: At most one holding reservation per fan and sale
**Reason**: Reservation is renamed Checkout, belongs to a TicketType instead of a TicketSale and no longer stores a holder name or phone number; the fan's full name and phone number are the User's.
**Migration**: The behavior continues in `components/entity/checkout/get-or-create-held`; the data moves in this change's migration.
