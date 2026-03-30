## ADDED Requirements

### Requirement: Poison Queue consumer emits ERROR logs

The backend event consumer SHALL subscribe to the `POISON` NATS JetStream stream and emit a structured ERROR log entry for every message it receives. The log entry MUST include the original topic/subject and message UUID to enable tracing.

#### Scenario: Message is routed to Poison Queue after max retries

- **WHEN** a Watermill handler fails after exhausting all retries and the message is routed to the `POISON` stream
- **THEN** the Poison Queue consumer SHALL receive the message
- **AND** SHALL emit an ERROR log entry with `msg="message routed to poison queue"`, the original `topic`, and the message `uuid`
- **AND** SHALL ack the message (it is not re-processed)

#### Scenario: Poison Queue consumer ERROR log triggers workload alert

- **WHEN** the Poison Queue consumer emits an ERROR log
- **THEN** the existing consumer workload alert policy (from `app-error-log-alerting`) SHALL detect the log entry
- **AND** SHALL open an Incident and send a Slack/Google Chat notification

#### Scenario: Consumer is scaled to zero when message is poisoned

- **WHEN** the consumer Pod is scaled to zero by KEDA and a message is routed to the Poison Queue
- **THEN** the message SHALL remain in the `POISON` stream until the consumer Pod scales back up
- **AND** on next consumer startup, the Poison Queue consumer SHALL process and log all pending messages

### Requirement: NATS POISON stream lag alert

The system SHALL have a Cloud Monitoring alert policy that detects accumulation of unprocessed messages in the NATS `POISON` stream.

The alert SHALL trigger when the POISON stream consumer lag exceeds 0 for more than 5 minutes, to allow for normal consumer startup delay after KEDA scale-up.

#### Scenario: Messages accumulate in POISON stream

- **WHEN** the NATS `POISON` stream has unprocessed messages for more than 5 minutes
- **THEN** the Cloud Monitoring alert policy SHALL open an Incident
- **AND** SHALL send a notification to the configured Slack and Google Chat channels

#### Scenario: POISON stream is empty

- **WHEN** the NATS `POISON` stream has zero pending messages
- **THEN** no alert SHALL fire

#### Scenario: Alert uses same notification channels as backend workload alerts

- **WHEN** the POISON stream lag alert fires
- **THEN** the notification SHALL be sent to the same Slack and Google Chat channels as the `app-error-log-alerting` workload alerts
- **AND** the same 12-hour notification rate limit SHALL apply
