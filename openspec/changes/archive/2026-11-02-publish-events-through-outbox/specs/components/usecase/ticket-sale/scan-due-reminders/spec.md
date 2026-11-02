## MODIFIED Requirements

### Requirement: Delivery is delegated to DeliverReminder

ScanDueReminders SHALL NOT deliver reminders or record them as sent; it SHALL start TicketSaleReminderDeliveryUseCase.DeliverReminder for each requested reminder, with its fan, sale, stage and content. Each start SHALL be named after the fan, the sale, the stage and the 15-minute period the run belongs to, so a run repeated in the same period starts no reminder twice, and a later run starts the reminder again while it is not recorded as sent.

#### Scenario: Reminder requested
- **WHEN** ScanDueReminders requests a reminder
- **THEN** DeliverReminder runs once for it and nothing is recorded as sent by the scan

#### Scenario: Run repeated in the same period
- **WHEN** the run of 18:30 is repeated at 18:37 and requests the same reminder again
- **THEN** DeliverReminder runs once for that fan, sale and stage

#### Scenario: Not yet recorded as sent
- **WHEN** the run of 18:30 requested a reminder whose push failed, and the run of 18:45 finds the stage still due and not recorded as sent
- **THEN** DeliverReminder runs again for that fan, sale and stage
