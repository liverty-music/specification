# Spec Delta

## REMOVED Requirements

### Requirement: Order of an application
**Reason**: Every ticketing record now names the User `user`, and TicketApplication is renamed LotteryEntry.
**Migration**: The behavior continues in `components/entity/order/get-by-lottery-entry-id`; the data moves in this change's migration.
