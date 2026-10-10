# Spec Delta

## REMOVED Requirements

### Requirement: Tickets of a holder
**Reason**: Every ticketing record now names the User `user`, and TicketApplication is renamed LotteryEntry.
**Migration**: The behavior continues in `components/entity/ticket/list-by-user`; the data moves in this change's migration.
