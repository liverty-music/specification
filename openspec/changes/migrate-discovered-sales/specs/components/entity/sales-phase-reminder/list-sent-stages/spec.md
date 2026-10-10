# Spec Delta

## REMOVED Requirements

### Requirement: ListSentStages returns the recorded stages per user
**Reason**: SalesPhaseReminder is renamed TicketSaleReminder and refers to a TicketSale, discovered or an Organizer's.
**Migration**: The behavior continues in `components/entity/ticket-sale-reminder/list-sent-stages`; the stored data moves in this change's migration.
