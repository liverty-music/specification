# Spec Delta

## REMOVED Requirements

### Requirement: Only the fan's own checkout, committed while holding
**Reason**: IssueFromReservation is renamed IssueFromCheckout; it issues from a Checkout of a TicketType, and the Tickets carry no copy of the user's name or phone number.
**Migration**: The behavior continues in `components/usecase/order/issue-from-checkout`; the data moves in this change's migration.

### Requirement: Charge once, then issue
**Reason**: IssueFromReservation is renamed IssueFromCheckout; it issues from a Checkout of a TicketType, and the Tickets carry no copy of the user's name or phone number.
**Migration**: The behavior continues in `components/usecase/order/issue-from-checkout`; the data moves in this change's migration.
