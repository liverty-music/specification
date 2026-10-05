# Spec Delta

## MODIFIED Requirements

### Requirement: Runs for each reminder the scan requests

DeliverReminder SHALL run for each reminder that ScanDueReminders requests, with the fan, the sales phase, the stage and the prepared content as input. A request without content SHALL be ignored without an error.

#### Scenario: Reminder requested

- **WHEN** ScanDueReminders requests an `APPLY_CLOSE_24H` reminder for a fan
- **THEN** DeliverReminder runs for that fan, phase and stage

#### Scenario: Empty request

- **WHEN** DeliverReminder receives a request without content
- **THEN** nothing is delivered and it succeeds
