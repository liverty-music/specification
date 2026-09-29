# Spec Delta

## MODIFIED Requirements

### Requirement: Follow announces the new follow

After a new Follow is stored, Follow SHALL announce that the fan followed the artist. The announcement is also what starts a first concert search for an artist that has never been searched (ConcertUseCase.SearchNewConcertsOnFirstFollow). A failure to announce SHALL NOT fail the follow; the artist is then not searched on this follow and is left to the daily concert search.

#### Scenario: New follow announced

- **WHEN** a fan follows an artist they do not follow
- **THEN** the follow is announced once, carrying the fan and the artist

#### Scenario: Announcement fails

- **WHEN** the follow is stored but announcing it fails
- **THEN** Follow still succeeds

## REMOVED Requirements

### Requirement: First concert search started in the background

**Reason**: Follow no longer reads the search history or starts a concert search. The first search is started by ConcertUseCase.SearchNewConcertsOnFirstFollow when the follow is announced; its spec states the never-searched check and its failure handling.

**Migration**: None for callers. The trigger is the follow announcement required by "Follow announces the new follow".
