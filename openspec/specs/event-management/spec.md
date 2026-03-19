# event-management Specification

## Purpose

The Event Management capability handles the lifecycle of generic events, providing a foundation for specific event types like concerts. It ensures consistent handling of common event data such as titles, dates, times, and venues.

## Requirements

### Requirement: Generic Event Management

The system SHALL support a generic `Event` entity that encapsulates common event properties: ID, Title, VenueID, LocalEventDate, StartTime, OpenTime, and SourceURL. The `EventId` message SHALL be defined in `event.proto` as the canonical event identifier for the platform.

#### Scenario: Event Persistence
- **WHEN** a generic event is created
- **THEN** it is persisted in the `events` table with a unique identifier
- **AND** it can be retrieved independently of specific event types (like Concerts)

#### Scenario: EventId is the canonical event identifier
- **WHEN** any entity or RPC references an event identifier
- **THEN** it SHALL use `EventId` from `event.proto`
- **AND** `EventId` SHALL NOT be defined in `ticket.proto` or any other file

#### Scenario: Concert uses EventId
- **WHEN** a `Concert` proto message is defined
- **THEN** its `id` field SHALL be of type `EventId` (not `ConcertId`)
- **AND** the `ConcertId` message SHALL NOT exist in the schema

### Requirement: Event-Type Extensibility

The system SHALL support extending the base `Event` entity with domain-specific entities (e.g., `Concert`) via a 1:1 relationship.

#### Scenario: Concert as Event
- **WHEN** a `Concert` is created
- **THEN** an associated `Event` record is strictly required
- **AND** the `Concert` record shares the same unique identifier (or references it as a foreign key with uniqueness constraint)

### Requirement: Trace context propagation across message broker

The system SHALL propagate W3C Trace Context (traceparent) from the publisher process to the consumer process via message metadata. Consumer-side structured logs SHALL include `trace_id` and `span_id` fields extracted from the propagated trace context.

#### Scenario: Consumer log includes trace fields from publisher trace

- **WHEN** a publisher emits an event while processing a traced request
- **THEN** the consumer handler's structured logs MUST contain `trace_id` and `span_id` fields matching the publisher's trace

#### Scenario: Consumer handler operates within propagated span

- **WHEN** the consumer receives a message with trace context in its metadata
- **THEN** all downstream operations (database queries, nested event publishing) MUST be children of the propagated trace
