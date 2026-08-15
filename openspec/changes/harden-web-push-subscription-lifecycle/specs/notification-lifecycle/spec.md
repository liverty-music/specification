## MODIFIED Requirements

### Requirement: Per-notification delivery outcome is recorded
The service SHALL record the delivery outcome of each notification's channel send: `queued` on creation, then `delivered` once the channel accepts the send, or `failed` (with a failure reason) on error, so that "did this notification reach the user?" is answerable from stored state. (Web push provides no separate sent-vs-delivered receipt, so `delivered` denotes acceptance by the push service; a distinct `sent` state is not modelled for this channel.)

In addition to persisting the outcome, a `failed` delivery SHALL be surfaced as an operational signal — logged at WARNING with the failure reason, and emitted as a delivery-outcome metric labelled by outcome and failure reason — so that a systemic delivery failure is observable without querying the database. A `failed` outcome SHALL NOT be observable only from stored state.

#### Scenario: Successful web-push send is recorded as delivered
- **WHEN** the web-push channel send for a notification succeeds
- **THEN** the notification's delivery status SHALL be recorded as `delivered` with a delivery timestamp

#### Scenario: Failed send is recorded as failed, not dropped
- **WHEN** the web-push channel send fails (e.g. the push service rejects it)
- **THEN** the notification's delivery status SHALL be recorded as `failed` with a failure reason
- **AND** the notification record SHALL remain so the failure is auditable and the send is re-dispatchable

#### Scenario: Failed send is surfaced as an operational signal
- **WHEN** a notification's delivery is recorded as `failed`
- **THEN** the service SHALL log the failure at WARNING including the failure reason
- **AND** SHALL emit a delivery-outcome metric labelled by outcome and failure reason
- **AND** the failure SHALL therefore be detectable without reading the notifications table

## ADDED Requirements

### Requirement: Notification fan-out logs zero-recipient skips
When the new-concert notification fan-out completes without dispatching any notification — because the artist has no followers, or because no follower is eligible after hype filtering, or because there are no deliverable concerts — the system SHALL log that outcome with the reason and the relevant identifiers (e.g., artist), instead of returning silently. This ensures "processed the event but sent nothing" is diagnosable from logs alone.

#### Scenario: Event processed but no eligible recipients
- **WHEN** a `CONCERT.created` event is processed
- **AND** the fan-out dispatches zero notifications
- **THEN** the system SHALL log the zero-dispatch outcome with its reason (no followers, no eligible recipients, or no deliverable concerts)
- **AND** the log SHALL include the artist identifier
- **AND** the processing SHALL still complete successfully (the empty outcome is not an error)
