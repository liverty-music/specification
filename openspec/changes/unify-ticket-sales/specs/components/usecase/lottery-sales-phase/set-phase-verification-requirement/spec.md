# Spec Delta

## REMOVED Requirements

### Requirement: Change the requirement at any time
**Reason**: LotterySalesPhase is replaced by TicketSale (the sale opportunity, which can cover several events of a Series) and TicketType (what it offers for one event).
**Migration**: The behavior continues in `components/usecase/ticket-sale/set-verification-requirement`; the data moves in this change's migration.

### Requirement: Only the event's Organizer changes the requirement
**Reason**: LotterySalesPhase is replaced by TicketSale (the sale opportunity, which can cover several events of a Series) and TicketType (what it offers for one event).
**Migration**: The behavior continues in `components/usecase/ticket-sale/set-verification-requirement`; the data moves in this change's migration.
