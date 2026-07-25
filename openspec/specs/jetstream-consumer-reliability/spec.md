# jetstream-consumer-reliability Specification

## Purpose
TBD - created by archiving change harden-jetstream-consumer-reliability. Update Purpose after archive.
## Requirements
### Requirement: Consumer backlog stall is detected and alerted

The system SHALL detect when any backend JetStream consumer stops draining its backlog and open an incident via Cloud Monitoring, independent of whether the consumer emits ERROR logs or poison messages.

The alert SHALL be based on the JetStream consumer backlog metric (`num_pending` / unprocessed message count, exposed by the NATS monitoring endpoint) and SHALL fire when a consumer's backlog stays above a threshold and is not decreasing for a sustained window.

#### Scenario: A consumer stops draining while events keep arriving

- **WHEN** a backend JetStream consumer's unprocessed backlog stays above the configured threshold and does not decrease for the configured window
- **THEN** a Cloud Monitoring alert policy SHALL open an incident naming the affected stream/consumer

#### Scenario: A healthy draining consumer does not alert

- **WHEN** a consumer's backlog rises transiently but is drained back down within the window
- **THEN** no incident SHALL be opened

#### Scenario: Silent stall with no ERROR log still alerts

- **WHEN** a consumer stops consuming without emitting any ERROR log or poison-queue message
- **THEN** the backlog alert SHALL still fire, because it depends on backlog metrics, not on logs

### Requirement: Subscription failure fails loud

The consumer SHALL treat a failure to establish any of its JetStream subscriptions at startup as fatal: it SHALL log the failure at ERROR level (identifying the topic) and SHALL fail startup rather than continuing to serve traffic with missing subscriptions.

#### Scenario: A durable cannot be created or bound at startup

- **WHEN** the consumer cannot create or bind the durable for one of its topics
- **THEN** it SHALL emit an ERROR log for that topic AND terminate startup (non-zero exit / crashloop) instead of reporting healthy

#### Scenario: One failing subscription does not silently disable the rest

- **WHEN** a single topic's subscription fails
- **THEN** the consumer SHALL NOT continue running with the remaining topics silently unsubscribed

### Requirement: Liveness reflects consumption health

The consumer's liveness and readiness probes SHALL report unhealthy when the message router is not running or when its expected durables are not actively bound, so that Kubernetes restarts a wedged pod instead of leaving it `Running`.

#### Scenario: Router is not consuming

- **WHEN** the message router has stopped or its expected durables are not bound to an active subscription
- **THEN** the liveness probe SHALL report unhealthy and Kubernetes SHALL restart the pod

#### Scenario: Fully consuming pod stays healthy

- **WHEN** the router is running and all expected durables are bound
- **THEN** the liveness and readiness probes SHALL report healthy

### Requirement: Durable configuration is reconciled on startup

The consumer SHALL reconcile each durable it owns against the desired configuration at startup. When a durable's server-stored configuration (name, deliver group, or delivery policy) has drifted from the desired configuration, the consumer SHALL recreate the durable so that a configuration or naming change cannot wedge on a stale pre-existing durable.

#### Scenario: A pre-existing durable has drifted configuration

- **WHEN** a durable exists on the server with a configuration that differs from the consumer's desired configuration
- **THEN** the consumer SHALL delete and recreate that durable to match the desired configuration before consuming

#### Scenario: An already-correct durable is left untouched

- **WHEN** a durable already matches the desired configuration
- **THEN** the consumer SHALL bind to it without deleting or recreating it

### Requirement: Consumers are named by behavior, with a unique deliver group

Each durable and its deliver group SHALL be named after the **behavior** (the handler / reaction) it performs, not after the subject it consumes — using a `<verb>-<object>` name from the controlled vocabulary `ingest`, `resolve`, `verify`, `notify`, `track`, `log` (e.g. `CONCERT.created` → `notify-concert`). Every consumer's deliver group SHALL equal its own durable name, so no two consumers ever share a deliver group.

#### Scenario: Durable is named for its behavior

- **WHEN** the consumer establishes the handler that pushes fans about a new concert (subject `CONCERT.created`)
- **THEN** its durable and deliver-group names SHALL both be `notify-concert` (the behavior), not the subject

#### Scenario: No two consumers share a deliver group

- **WHEN** any two consumers exist
- **THEN** each SHALL have a deliver group equal to its own durable name, so they cannot load-balance each other's messages

### Requirement: Every handler receives every message (fan-out)

When two or more handlers react to the same subject, each SHALL be an independent consumer that receives every matching message; handlers on the same subject SHALL NOT share a consumer or deliver group (which would silently load-balance the subject's messages between them).

#### Scenario: Two behaviors on one subject both run

- **WHEN** subject `ARTIST.created` has both a name-resolution handler and an image-resolution handler
- **THEN** each SHALL have its own consumer (`resolve-artist-name`, `resolve-artist-image`) and both SHALL process every `ARTIST.created` message

### Requirement: Subjects are named as past-tense events

Subjects SHALL be named `<DOMAIN>.<event_past_tense>`, describing what happened. Multi-token event names SHALL use underscores within the trailing token (e.g. `SALES_PHASE.reminder_due`), and an authentication login SHALL be modelled as `USER.logged_in` rather than a separate `ACCOUNT` domain.

#### Scenario: Login is a user event

- **WHEN** a login event is published
- **THEN** its subject SHALL be `USER.logged_in` on the `USER` stream, and no separate `ACCOUNT` stream SHALL be required

### Requirement: KEDA triggers reference the live behavior-named durables

The consumer autoscaler (KEDA ScaledObject) triggers SHALL reference the same behavior-named durables the application actually creates, so autoscaling reads the real backlog.

#### Scenario: Trigger name matches the live durable

- **WHEN** the consumer creates a durable for a behavior
- **THEN** the corresponding KEDA trigger SHALL reference that exact durable name

