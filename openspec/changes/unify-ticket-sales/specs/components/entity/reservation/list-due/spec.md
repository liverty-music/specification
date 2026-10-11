# Spec Delta

## REMOVED Requirements

### Requirement: Lapsed holds, card holds to give back and stalled commits
**Reason**: Reservation is renamed Checkout, belongs to a TicketType instead of a TicketSale and no longer stores a holder name or phone number; the fan's full name and phone number are the User's.
**Migration**: The behavior continues in `components/entity/checkout/list-due`; the data moves in this change's migration.
