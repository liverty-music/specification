## MODIFIED Requirements

### Requirement: Remove only empty candidates

DeleteOrphaned SHALL remove each given Series that has no Event, no ConcertCandidate and no TicketSale, SHALL leave every other Series — given or not — unchanged, and SHALL return how many it removed. A Series that another change is writing at that moment SHALL be left. An empty set SHALL remove nothing. Repeating it SHALL remove nothing more.

#### Scenario: Empty series removed
- **WHEN** a given Series has no Event, no ConcertCandidate and no TicketSale
- **THEN** it is removed

#### Scenario: Series with a concert candidate kept
- **WHEN** a given Series has no Event but one ConcertCandidate
- **THEN** it is kept

#### Scenario: Series with a ticket sale kept
- **WHEN** a given Series has no Event and no ConcertCandidate but one TicketSale
- **THEN** it is kept

#### Scenario: Series not given
- **WHEN** an empty Series was not among those given
- **THEN** it is kept
