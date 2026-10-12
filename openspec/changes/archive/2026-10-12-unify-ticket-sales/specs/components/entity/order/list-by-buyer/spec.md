# Spec Delta

## REMOVED Requirements

### Requirement: ListByBuyer returns the User's Orders
**Reason**: Every ticketing record now names the User `user`, and TicketApplication is renamed LotteryEntry.
**Migration**: The behavior continues in `components/entity/order/list-by-user`; the data moves in this change's migration.
