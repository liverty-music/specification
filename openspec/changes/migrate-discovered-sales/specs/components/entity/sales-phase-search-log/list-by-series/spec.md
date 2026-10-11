# Spec Delta

## REMOVED Requirements

### Requirement: Returns the logs that exist
**Reason**: SalesPhaseSearchLog is renamed TicketSaleSearch, as the sales it searches for are TicketSales.
**Migration**: The behavior continues in `components/entity/ticket-sale-search/list-by-series`; the stored data moves in this change's migration.
