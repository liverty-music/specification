# Spec Delta

## REMOVED Requirements

### Requirement: Won applications without an order
**Reason**: Every ticketing record now names the User `user`, and TicketApplication is renamed LotteryEntry.
**Migration**: The behavior continues in `components/entity/order/list-lottery-entry-ids-awaiting-issuance`; the data moves in this change's migration.
