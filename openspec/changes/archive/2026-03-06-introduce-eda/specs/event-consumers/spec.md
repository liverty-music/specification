# Capability: Event Consumers

## Purpose

Define the consumer handlers that react to concert discovery pipeline events, and the unified consumer process that hosts them.

## Requirements

### Requirement: Unified Consumer Process

The system SHALL provide a single long-running consumer process (`cmd/consumer/main.go`) that hosts all event handlers via a Watermill Router.

#### Scenario: Process startup

- **WHEN** the consumer process starts
- **THEN** it SHALL initialize a Watermill Router with all registered handlers
- **AND** connect to NATS JetStream as a subscriber
- **AND** connect to Cloud SQL PostgreSQL for data persistence
- **AND** listen for SIGINT/SIGTERM for graceful shutdown

#### Scenario: Graceful shutdown

- **WHEN** the consumer process receives SIGINT or SIGTERM
- **THEN** it SHALL stop accepting new messages
- **AND** wait for in-flight handlers to complete
- **AND** close all resources (NATS connection, database pool, telemetry)

#### Scenario: Kubernetes deployment

- **WHEN** the consumer is deployed to GKE
- **THEN** it SHALL run as a Deployment in the `backend` namespace
- **AND** reuse the existing `backend-app` GCP service account via Workload Identity

### Requirement: create-concerts Handler

The system SHALL provide a handler that persists discovered concerts and their venues from `concert.discovered.v1` events.

#### Scenario: New concert with existing venue

- **WHEN** a `concert.discovered.v1` event is received
- **AND** the batch contains a concert whose venue already exists in the database (matched by name or raw_name)
- **THEN** the handler SHALL create the concert record linked to the existing venue
- **AND** the concert SHALL be included in the subsequent `concert.created.v1` event

#### Scenario: New concert with new venue

- **WHEN** a `concert.discovered.v1` event is received
- **AND** the batch contains a concert whose venue does not exist in the database
- **THEN** the handler SHALL create a new venue record with `enrichment_status = 'pending'`
- **AND** publish a `liverty-music.venue.created.v1` event with the venue ID, raw name, and admin area
- **AND** create the concert record linked to the new venue

#### Scenario: Duplicate concert in batch is skipped

- **WHEN** a `concert.discovered.v1` event is received
- **AND** a concert in the batch already exists in the database (matched by artist_id + local_date + start_time)
- **THEN** the handler SHALL skip that concert without error
- **AND** it SHALL NOT be included in the `concert.created.v1` event

#### Scenario: Venue creation race condition

- **WHEN** the handler attempts to create a venue
- **AND** a concurrent handler has already created the same venue (AlreadyExists error)
- **THEN** the handler SHALL fetch the existing venue and use it

#### Scenario: Batch result event

- **WHEN** all concerts in a `concert.discovered.v1` event have been processed
- **AND** at least one new concert was created
- **THEN** the handler SHALL publish a `liverty-music.concert.created.v1` event containing the artist ID, list of created concert IDs, and the count

#### Scenario: No new concerts after deduplication

- **WHEN** all concerts in a `concert.discovered.v1` event are duplicates
- **THEN** the handler SHALL NOT publish a `concert.created.v1` event
- **AND** the message SHALL be acknowledged successfully

### Requirement: notify-fans Handler

The system SHALL provide a handler that sends push notifications to artist followers when new concerts are created.

#### Scenario: Notification on concert creation

- **WHEN** a `concert.created.v1` event is received
- **THEN** the handler SHALL call `PushNotificationUseCase.NotifyNewConcerts` with the artist and the created concerts
- **AND** the notification body SHALL read "{count} new concerts found"

#### Scenario: Notification failure is non-fatal

- **WHEN** `NotifyNewConcerts` returns an error
- **THEN** the handler SHALL log the error
- **AND** the message SHALL still be acknowledged (notification delivery is best-effort)

### Requirement: enrich-venue Handler

The system SHALL provide a handler that enriches newly created venues via external place services.

#### Scenario: Venue enrichment triggered by event

- **WHEN** a `liverty-music.venue.created.v1` event is received
- **THEN** the handler SHALL call the venue enrichment logic for that specific venue
- **AND** follow the existing enrichment pipeline (MusicBrainz → Google Maps fallback)

#### Scenario: Transient enrichment failure

- **WHEN** the enrichment encounters a transient error (network, rate limit)
- **THEN** the handler SHALL return an error to trigger NATS redelivery
- **AND** the venue SHALL remain in `pending` status

#### Scenario: Permanent enrichment failure

- **WHEN** all external sources return no match
- **THEN** the handler SHALL mark the venue as `failed`
- **AND** acknowledge the message
