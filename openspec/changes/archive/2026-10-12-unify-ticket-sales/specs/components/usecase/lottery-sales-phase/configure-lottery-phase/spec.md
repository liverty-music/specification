# Spec Delta

## REMOVED Requirements

### Requirement: Configure a phase for a published event
**Reason**: LotterySalesPhase is replaced by TicketSale (the sale opportunity, which can cover several events of a Series) and TicketType (what it offers for one event).
**Migration**: The behavior continues in `components/usecase/ticket-sale/create`; the data moves in this change's migration.

### Requirement: Only the event's Organizer configures its phases
**Reason**: LotterySalesPhase is replaced by TicketSale (the sale opportunity, which can cover several events of a Series) and TicketType (what it offers for one event).
**Migration**: The behavior continues in `components/usecase/ticket-sale/create`; the data moves in this change's migration.
