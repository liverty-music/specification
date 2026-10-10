# Spec Delta

## REMOVED Requirements

### Requirement: Runs for each reminder the scan requests
**Reason**: Delivery now records TicketSaleReminders, as TicketSaleReminderDeliveryUseCase.DeliverReminder.
**Migration**: The behavior continues in `components/usecase/ticket-sale-reminder/deliver-reminder`; the stored data moves in this change's migration.

### Requirement: A reminder already sent is not delivered again
**Reason**: Delivery now records TicketSaleReminders, as TicketSaleReminderDeliveryUseCase.DeliverReminder.
**Migration**: The behavior continues in `components/usecase/ticket-sale-reminder/deliver-reminder`; the stored data moves in this change's migration.

### Requirement: One sales reminder notification per reminder
**Reason**: Delivery now records TicketSaleReminders, as TicketSaleReminderDeliveryUseCase.DeliverReminder.
**Migration**: The behavior continues in `components/usecase/ticket-sale-reminder/deliver-reminder`; the stored data moves in this change's migration.

### Requirement: The reminder is recorded as sent only when it reached the fan or cannot
**Reason**: Delivery now records TicketSaleReminders, as TicketSaleReminderDeliveryUseCase.DeliverReminder.
**Migration**: The behavior continues in `components/usecase/ticket-sale-reminder/deliver-reminder`; the stored data moves in this change's migration.
