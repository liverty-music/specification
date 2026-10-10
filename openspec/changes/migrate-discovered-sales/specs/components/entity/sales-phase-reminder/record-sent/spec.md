# Spec Delta

## REMOVED Requirements

### Requirement: At most one record per user, sales phase and stage
**Reason**: SalesPhaseReminder is renamed TicketSaleReminder and refers to a TicketSale, discovered or an Organizer's.
**Migration**: The behavior continues in `components/entity/ticket-sale-reminder/record-sent`; the stored data moves in this change's migration.

### Requirement: RecordSent validates its input
**Reason**: SalesPhaseReminder is renamed TicketSaleReminder and refers to a TicketSale, discovered or an Organizer's.
**Migration**: The behavior continues in `components/entity/ticket-sale-reminder/record-sent`; the stored data moves in this change's migration.
