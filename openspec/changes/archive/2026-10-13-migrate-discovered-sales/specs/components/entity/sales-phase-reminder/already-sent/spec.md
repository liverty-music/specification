# Spec Delta

## REMOVED Requirements

### Requirement: AlreadySent reports an existing record
**Reason**: SalesPhaseReminder is renamed TicketSaleReminder and refers to a TicketSale, discovered or an Organizer's.
**Migration**: The behavior continues in `components/entity/ticket-sale-reminder/already-sent`; the stored data moves in this change's migration.
