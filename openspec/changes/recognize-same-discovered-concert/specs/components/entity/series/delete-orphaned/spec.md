## MODIFIED Requirements

### Requirement: Remove only empty candidates

DeleteOrphaned SHALL remove each given Series that has no Event, no ConcertCandidate and no TicketSale, SHALL leave every other Series — given or not — unchanged, and SHALL return how many it removed. A given Series under which a concurrent change is still storing an Event, a ConcertCandidate or a TicketSale SHALL be left. An empty set SHALL remove nothing. When no change was in progress during a call and nothing has changed since, repeating it SHALL remove nothing more.

#### Scenario: Empty series removed
- **WHEN** a given Series has no Event, no ConcertCandidate and no TicketSale
- **THEN** it is removed

#### Scenario: Series with a concert candidate kept
- **WHEN** a given Series has no Event but one ConcertCandidate
- **THEN** it is kept

#### Scenario: Series with a ticket sale kept
- **WHEN** a given Series has no Event and no ConcertCandidate but one TicketSale
- **THEN** it is kept

#### Scenario: Series still being written
- **WHEN** a TicketSale is still being stored for a given Series that has no Event
- **THEN** it is kept

#### Scenario: Series not given
- **WHEN** an empty Series was not among those given
- **THEN** it is kept
