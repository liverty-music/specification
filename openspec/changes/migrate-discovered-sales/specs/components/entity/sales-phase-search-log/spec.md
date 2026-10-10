# Spec Delta

## REMOVED Requirements

### Requirement: Searched time is not in the future
**Reason**: SalesPhaseSearchLog is renamed TicketSaleSearchLog, as the sales it searches for are TicketSales.
**Migration**: The behavior continues in `components/entity/ticket-sale-search-log`; the stored data moves in this change's migration.
