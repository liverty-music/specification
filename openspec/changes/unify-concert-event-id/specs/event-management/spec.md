## MODIFIED Requirements

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
