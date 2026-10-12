# Spec Delta

## REMOVED Requirements

### Requirement: Phases due for draw
**Reason**: LotterySalesPhase is replaced by TicketSale (the sale opportunity, which can cover several events of a Series) and TicketType (what it offers for one event).
**Migration**: The behavior continues in `components/entity/ticket-sale/list-due-for-draw`; the data moves in this change's migration.
