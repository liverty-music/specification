# Spec Delta

## REMOVED Requirements

### Requirement: Returns every phase of the series
**Reason**: SalesPhase is merged into TicketSale: a discovered sale is a TicketSale of a Series without an Organizer, offering no TicketType.
**Migration**: The behavior continues in `components/entity/ticket-sale/list-by-series`; the stored data moves in this change's migration.

### Requirement: A series is required
**Reason**: SalesPhase is merged into TicketSale: a discovered sale is a TicketSale of a Series without an Organizer, offering no TicketType.
**Migration**: The behavior continues in `components/entity/ticket-sale/list-by-series`; the stored data moves in this change's migration.
