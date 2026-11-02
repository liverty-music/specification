## MODIFIED Requirements

### Requirement: Runs for each reminder the scan requests

DeliverReminder SHALL run when TicketSaleReminderUseCase.ScanDueReminders starts it for a reminder, with the fan, the TicketSale, the stage and the prepared content as input, once per fan, sale, stage and scan period. A request without content SHALL be ignored without an error.

#### Scenario: Reminder requested
- **WHEN** ScanDueReminders starts an `APPLY_CLOSE_24H` reminder for a fan
- **THEN** DeliverReminder runs for that fan, sale and stage

#### Scenario: Empty request
- **WHEN** DeliverReminder receives a request without content
- **THEN** nothing is delivered and it succeeds
