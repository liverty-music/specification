## ADDED Requirements

### Requirement: Trigger Concert Discovery

The system SHALL provide an interface to trigger the discovery of new concerts for a specific artist.

#### Scenario: Successful Search

- **WHEN** `SearchNewConcerts` is called with a valid `artist_id`
- **THEN** the system MUST execute the concert discovery process
- **AND** return a list of newly discovered concerts that were not previously in the system.

#### Scenario: Missing Artist ID

- **WHEN** `SearchNewConcerts` is called without an `artist_id`
- **THEN** the system MUST return an `INVALID_ARGUMENT` error.
