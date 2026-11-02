## MODIFIED Requirements

### Requirement: Runs for each announced follow

SearchNewConcertsOnFirstFollow SHALL run once for each new Follow that Follow.Follow announces, with the followed Artist. A follow that is not announced starts nothing here; Follow.Follow states when a follow is announced.

#### Scenario: Follow announced

- **WHEN** a fan's new Follow of an Artist is announced
- **THEN** SearchNewConcertsOnFirstFollow runs for that Artist
