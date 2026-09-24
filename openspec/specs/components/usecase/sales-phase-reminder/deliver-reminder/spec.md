# Deliver Reminder

## Purpose

DeliverReminder issues one due sales-phase reminder (one fan, one phase, one stage) as a notification to that fan. It first checks that this reminder has not already been sent, and it records the reminder as sent only after delivery succeeds or when the fan has no device.

## Requirements

### Requirement: Runs for each reminder the scan requests

DeliverReminder SHALL run for each reminder that ScanDueReminders requests, with the fan, the sales phase, the stage and the prepared content as input. A request without content SHALL be ignored without an error.

#### Scenario: Reminder requested

- **WHEN** ScanDueReminders requests an `APPLY_CLOSE_1H` reminder for a fan
- **THEN** DeliverReminder runs for that fan, phase and stage

#### Scenario: Empty request

- **WHEN** DeliverReminder receives a request without content
- **THEN** nothing is delivered and it succeeds

### Requirement: A reminder already sent is not delivered again

DeliverReminder SHALL first call SalesPhaseReminder.AlreadySent and deliver nothing when the reminder is already recorded as sent. When that check fails, DeliverReminder SHALL fail so the request runs again.

#### Scenario: Repeated request

- **WHEN** DeliverReminder receives a reminder that is already recorded as sent to the fan
- **THEN** nothing is delivered and it succeeds

#### Scenario: Check fails

- **WHEN** AlreadySent fails
- **THEN** DeliverReminder fails and the request runs again

### Requirement: One sales reminder notification per reminder

DeliverReminder SHALL issue one notification of type sales reminder to the fan, carrying the prepared content, and read its delivery outcome. When the notification cannot be recorded, DeliverReminder SHALL fail so the request runs again. The story stories/get-reminded-of-ticket-sale-milestones covers the whole flow from the due milestone to the fan's device.

#### Scenario: Delivered to a device

- **WHEN** DeliverReminder runs for a fan
- **THEN** one sales reminder notification is issued for the fan with the prepared content

### Requirement: The reminder is recorded as sent only when it reached the fan or cannot

DeliverReminder SHALL call SalesPhaseReminder.RecordSent when the notification's outcome is Delivered, or Failed because the fan has no registered device. On any other failed outcome it SHALL record nothing, so a later scan requests the reminder again. When recording fails after a successful delivery, DeliverReminder SHALL still succeed; a later scan may then deliver the reminder again, and the repeat replaces the earlier one on the device.

#### Scenario: Accepted by a device

- **WHEN** the notification's outcome is Delivered
- **THEN** the reminder is recorded as sent

#### Scenario: No device

- **WHEN** the notification's outcome is Failed because the fan has no registered device
- **THEN** the reminder is recorded as sent

#### Scenario: Push fails

- **WHEN** the notification's outcome is Failed for any other reason
- **THEN** nothing is recorded and a later scan requests the reminder again

#### Scenario: Recording fails after delivery

- **WHEN** the reminder was delivered and RecordSent fails
- **THEN** DeliverReminder succeeds and a later scan may deliver the reminder again
