# Capability: Event Messaging

## Purpose

Provide a persistent, at-least-once messaging infrastructure for asynchronous event-driven communication between backend components, using NATS JetStream as the transport and Watermill as the Go abstraction layer.

## Requirements

### Requirement: NATS JetStream Cluster

The system SHALL run a NATS JetStream cluster on GKE as the messaging backbone for all domain events.

#### Scenario: High-availability deployment

- **WHEN** the NATS cluster is deployed to production
- **THEN** it SHALL consist of 3 replicas with JetStream enabled
- **AND** each replica SHALL use a PersistentVolumeClaim with `premium-rwo` StorageClass for message persistence

#### Scenario: Dedicated namespace

- **WHEN** the NATS cluster is deployed
- **THEN** it SHALL run in a dedicated `nats` namespace
- **AND** it SHALL be managed by an ArgoCD Application using the official NATS Helm chart

### Requirement: JetStream Streams Per Domain Aggregate

The system SHALL use one JetStream stream per domain aggregate, following the NATS best practice of domain-scoped streams with subject hierarchies.

#### Scenario: CONCERT stream configuration

- **WHEN** the stream `CONCERT` is created
- **THEN** it SHALL subscribe to subjects matching `CONCERT.*`
- **AND** retention SHALL be `Limits` with a max age of 7 days
- **AND** storage SHALL be `File` with 3 replicas
- **AND** discard policy SHALL be `Old`

#### Scenario: VENUE stream configuration

- **WHEN** the stream `VENUE` is created
- **THEN** it SHALL subscribe to subjects matching `VENUE.*`
- **AND** retention, storage, and discard policy SHALL match the CONCERT stream

#### Scenario: Stream naming conventions

- **GIVEN** NATS JetStream stream names prohibit `.`, `>`, `*`, spaces, and path separators
- **THEN** stream names SHALL be UPPER_CASE alphanumeric (e.g., `CONCERT`, `VENUE`)
- **AND** subjects SHALL use the pattern `<STREAM>.<event_name>` (e.g., `CONCERT.discovered`, `CONCERT.created`, `VENUE.created`)

#### Scenario: Stream provisioning

- **WHEN** streams are deployed
- **THEN** they SHALL be pre-created via NATS Helm values or init configuration
- **AND** the Watermill publisher/subscriber SHALL use `AutoProvision: false`

### Requirement: Event Subjects

All domain events SHALL be published to NATS subjects following the `<STREAM>.<event_name>` convention.

#### Scenario: Concert domain events

- **WHEN** a concert discovery job finds new concerts
- **THEN** it SHALL publish to subject `CONCERT.discovered`
- **WHEN** a concert entity is persisted to the database
- **THEN** it SHALL publish to subject `CONCERT.created`

#### Scenario: Venue domain events

- **WHEN** a new venue entity is created
- **THEN** it SHALL publish to subject `VENUE.created`

### Requirement: Event Envelope

All events published through the messaging system SHALL include structured metadata as Watermill message metadata.

#### Scenario: Event metadata

- **WHEN** an event is published
- **THEN** the Watermill message metadata SHALL include `ce_specversion` set to `"1.0"`
- **AND** `ce_source` identifying the publishing component
- **AND** `ce_id` as a unique identifier (UUIDv7)
- **AND** `ce_time` as an RFC 3339 timestamp
- **AND** `ce_datacontenttype` set to `"application/json"`

#### Scenario: Event payload

- **WHEN** an event is published
- **THEN** the Watermill message payload SHALL be a JSON-serialized Go struct

### Requirement: Watermill Publisher Abstraction

The system SHALL use Watermill's `message.Publisher` interface for all event publishing, enabling transport-agnostic code.

#### Scenario: Production environment

- **WHEN** the application runs with `NATS_URL` configured
- **THEN** the DI layer SHALL initialize a Watermill NATS JetStream publisher

#### Scenario: Local development

- **WHEN** the application runs without `NATS_URL` (local environment)
- **THEN** the DI layer SHALL initialize a Watermill GoChannel publisher with `FanOut: true`

### Requirement: Watermill Router Middleware

The consumer process SHALL use a Watermill Router with standard middleware for operational resilience.

#### Scenario: Retry middleware

- **WHEN** a handler returns an error
- **THEN** the Watermill Router SHALL retry the handler up to a configured maximum (per consumer)
- **AND** use exponential backoff between retries

#### Scenario: Poison queue middleware

- **WHEN** a message exceeds the maximum retry count
- **THEN** the Router SHALL publish the message to a poison queue topic
- **AND** log the failure with the original topic, message ID, and error

#### Scenario: Logging and tracing middleware

- **WHEN** a message is processed by a handler
- **THEN** the Router SHALL log the topic, message ID, and processing duration
- **AND** propagate OpenTelemetry trace context from the message metadata

### Requirement: KEDA Autoscaling

The consumer Deployment SHALL be autoscaled by KEDA based on NATS JetStream consumer lag.

#### Scenario: Scale up on lag

- **WHEN** the pending message count for a NATS consumer exceeds the configured threshold
- **THEN** KEDA SHALL increase the number of consumer pods up to `maxReplicaCount`

#### Scenario: Scale down on idle

- **WHEN** the pending message count drops to zero
- **THEN** KEDA SHALL scale the consumer Deployment down to `minReplicaCount`

#### Scenario: KEDA deployment

- **WHEN** KEDA is deployed
- **THEN** it SHALL run in a dedicated `keda` namespace
- **AND** it SHALL be managed by an ArgoCD Application using the official KEDA Helm chart
