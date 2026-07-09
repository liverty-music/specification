## ADDED Requirements

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

### Requirement: Durable names carry no consumer-app prefix

Durable and deliver-group names SHALL be derived from the subject alone, per subject, without an app-level prefix (e.g. `CONCERT.created` maps to `CONCERT_created`). Because all event consumption is performed by the single consumer application, an app prefix carries no information.

#### Scenario: Durable name is derived from the subject only

- **WHEN** the consumer subscribes to subject `CONCERT.created`
- **THEN** the durable and deliver-group names SHALL be `CONCERT_created` with no additional prefix

#### Scenario: Each subject keeps a unique deliver group

- **WHEN** two different subjects reside in the same stream
- **THEN** each SHALL use its own per-subject deliver group so their consumers cannot collide

### Requirement: KEDA triggers reference the live durable names

The consumer autoscaler (KEDA ScaledObject) triggers SHALL reference the same durable/consumer names the application actually creates, so autoscaling reads the real backlog.

#### Scenario: Trigger name matches the live durable

- **WHEN** the consumer creates a durable for a subject
- **THEN** the corresponding KEDA trigger SHALL reference that exact durable name
