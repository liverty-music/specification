# Spec Delta

## REMOVED Requirements

### Requirement: A phase without a known start is skipped
**Reason**: SalesPhase is merged into TicketSale: a discovered sale is a TicketSale of a Series without an Organizer, offering no TicketType.
**Migration**: The behavior continues in `components/entity/ticket-sale/upsert-discovered`; the stored data moves in this change's migration.

### Requirement: Upsert never removes a phase
**Reason**: SalesPhase is merged into TicketSale: a discovered sale is a TicketSale of a Series without an Organizer, offering no TicketType.
**Migration**: The behavior continues in `components/entity/ticket-sale/upsert-discovered`; the stored data moves in this change's migration.

### Requirement: Upsert rejects a phase without a valid series
**Reason**: SalesPhase is merged into TicketSale: a discovered sale is a TicketSale of a Series without an Organizer, offering no TicketType.
**Migration**: The behavior continues in `components/entity/ticket-sale/upsert-discovered`; the stored data moves in this change's migration.

### Requirement: Same series, method and apply start date is the same sales phase
**Reason**: SalesPhase is merged into TicketSale: a discovered sale is a TicketSale of a Series without an Organizer, offering no TicketType.
**Migration**: The behavior continues in `components/entity/ticket-sale/upsert-discovered`; the stored data moves in this change's migration.
