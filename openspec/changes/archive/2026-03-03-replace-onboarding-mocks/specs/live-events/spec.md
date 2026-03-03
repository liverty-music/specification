## MODIFIED Requirements

### Requirement: Live Event Availability Check

The system SHALL provide a mechanism to check whether an artist has upcoming live events by querying the `ConcertService/List` RPC. This replaces the previous hash-based mock implementation.

#### Scenario: Artist has upcoming events

- **WHEN** `checkLiveEvents` is called with an artist ID
- **AND** `ConcertService/List` returns one or more concerts for that artist
- **THEN** the system SHALL return `true`

#### Scenario: Artist has no upcoming events

- **WHEN** `checkLiveEvents` is called with an artist ID
- **AND** `ConcertService/List` returns an empty list
- **THEN** the system SHALL return `false`

#### Scenario: Concert list call fails

- **WHEN** `checkLiveEvents` is called with an artist ID
- **AND** the `ConcertService/List` RPC call fails
- **THEN** the system SHALL return `false`
- **AND** the system SHALL log the error
