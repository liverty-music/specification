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

### Requirement: Single JetStream Stream

The system SHALL use a single JetStream stream for all domain events.

#### Scenario: Stream configuration

- **WHEN** the stream `LIVERTY_MUSIC` is created
- **THEN** it SHALL subscribe to subjects matching `liverty-music.>`
- **AND** retention SHALL be `Limits` with a max age of 7 days
- **AND** storage SHALL be `File` with 3 replicas
- **AND** discard policy SHALL be `Old`

### Requirement: CloudEvents Envelope

All events published through the messaging system SHALL conform to the CloudEvents v1.0 specification.

#### Scenario: Event metadata headers

- **WHEN** an event is published
- **THEN** the Watermill message metadata SHALL include `ce-specversion` set to `"1.0"`
- **AND** `ce-type` in the format `liverty-music.<aggregate>.<past-tense-verb>.v1`
- **AND** `ce-source` identifying the publishing component (e.g., `/api/artist-service`, `/job/concert-discovery`)
- **AND** `ce-id` as a unique identifier
- **AND** `ce-time` as an RFC 3339 timestamp
- **AND** `ce-datacontenttype` set to `"application/json"`

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
- **THEN** the Router SHALL publish the message to a poison queue topic (`liverty-music._poison`)
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
