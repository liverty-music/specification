# Spec Delta

## REMOVED Requirements

### Requirement: Phases are selected by opening time and latest milestone
**Reason**: SalesPhase is merged into TicketSale: a discovered sale is a TicketSale of a Series without an Organizer, offering no TicketType.
**Migration**: The behavior continues in `components/entity/ticket-sale/list-with-pending-milestones`; the stored data moves in this change's migration.

### Requirement: The window arguments are validated
**Reason**: SalesPhase is merged into TicketSale: a discovered sale is a TicketSale of a Series without an Organizer, offering no TicketType.
**Migration**: The behavior continues in `components/entity/ticket-sale/list-with-pending-milestones`; the stored data moves in this change's migration.
