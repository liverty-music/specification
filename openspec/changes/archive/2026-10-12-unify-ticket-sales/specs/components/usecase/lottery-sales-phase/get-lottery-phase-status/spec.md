# Spec Delta

## REMOVED Requirements

### Requirement: Phase with its tallies
**Reason**: LotterySalesPhase is replaced by TicketSale (the sale opportunity, which can cover several events of a Series) and TicketType (what it offers for one event).
**Migration**: The behavior continues in `components/usecase/ticket-sale/list-own-by-event`; the data moves in this change's migration.

### Requirement: Only the event's Organizer sees the status
**Reason**: LotterySalesPhase is replaced by TicketSale (the sale opportunity, which can cover several events of a Series) and TicketType (what it offers for one event).
**Migration**: The behavior continues in `components/usecase/ticket-sale/list-own-by-event`; the data moves in this change's migration.
