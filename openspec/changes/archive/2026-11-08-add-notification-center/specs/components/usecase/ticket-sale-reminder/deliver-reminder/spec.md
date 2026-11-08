## MODIFIED Requirements

### Requirement: Runs for each reminder the scan requests

DeliverReminder SHALL run when TicketSaleReminderUseCase.ScanDueReminders starts it for a reminder, with the fan, the TicketSale, the stage and the fan's linked event as input, once per fan, sale, stage and scan period. A request without a linked event SHALL be ignored without an error.

#### Scenario: Reminder requested
- **WHEN** ScanDueReminders starts an `APPLY_CLOSE_24H` reminder for a fan
- **THEN** DeliverReminder runs for that fan, sale and stage

#### Scenario: Empty request
- **WHEN** DeliverReminder receives a request without a linked event
- **THEN** nothing is delivered and it succeeds

### Requirement: One sales reminder notification per reminder

DeliverReminder SHALL issue one notification of type sales_reminder to the fan, whose subject is the TicketSale, the stage and the fan's linked event, and read the delivery outcome NotificationUseCase.Deliver returns. When the notification cannot be recorded, DeliverReminder SHALL fail so the request runs again. The story stories/get-reminded-of-ticket-sale-milestones covers the whole flow from the due milestone to the fan's device.

#### Scenario: Delivered to a device
- **WHEN** DeliverReminder runs for a fan
- **THEN** one sales_reminder notification is issued for the fan naming the sale, the stage and the fan's linked event
