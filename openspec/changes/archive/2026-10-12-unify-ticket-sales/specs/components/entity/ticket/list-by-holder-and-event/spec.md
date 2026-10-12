# Spec Delta

## REMOVED Requirements

### Requirement: Tickets of a holder for an event
**Reason**: Every ticketing record now names the User `user`; "holder" is not an entity.
**Migration**: The behavior continues in `components/entity/ticket/list-by-user-and-event`; the data moves in this change's migration.
