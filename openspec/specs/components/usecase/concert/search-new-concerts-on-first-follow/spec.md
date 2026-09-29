# components/usecase/concert/search-new-concerts-on-first-follow Specification

## Purpose
ConcertUseCase.SearchNewConcertsOnFirstFollow starts the first concert search for an Artist when a fan's new follow of it is announced and the Artist has never been searched, so the concerts of a newly followed Artist reach the catalog without waiting for the daily search.

## Requirements

### Requirement: Runs for each announced follow

SearchNewConcertsOnFirstFollow SHALL run once for each new Follow that FollowUseCase.Follow announces, with the followed Artist. A follow that is not announced starts nothing here; FollowUseCase.Follow states when a follow is announced.

#### Scenario: Follow announced

- **WHEN** a fan's new Follow of an Artist is announced
- **THEN** SearchNewConcertsOnFirstFollow runs for that Artist

### Requirement: Only a never-searched Artist is searched

SearchNewConcertsOnFirstFollow SHALL read the Artist's SearchLog (SearchLog.GetByArtistID). When the Artist has never been searched (NotFound), it SHALL run SearchNewConcerts for the Artist. When a SearchLog exists, whatever its status, it SHALL start no search and succeed. When several fans' follows of the same never-searched Artist are announced together, the search may run for each of them; SearchNewConcerts keeps the concerts it finds from being stored twice.

#### Scenario: Artist never searched

- **WHEN** SearchNewConcertsOnFirstFollow runs for an Artist with no SearchLog
- **THEN** SearchNewConcerts runs for the Artist

#### Scenario: Artist searched before

- **WHEN** SearchNewConcertsOnFirstFollow runs for an Artist that has a SearchLog
- **THEN** no search starts and SearchNewConcertsOnFirstFollow succeeds

### Requirement: A failure is retried without affecting the follow

When the SearchLog cannot be read for a reason other than NotFound, SearchNewConcertsOnFirstFollow SHALL fail without searching, and when SearchNewConcerts fails, SearchNewConcertsOnFirstFollow SHALL fail with that error, so the announced follow is processed again. A retry after SearchNewConcerts has recorded the Artist's SearchLog SHALL start no search, because the Artist has then been searched. The Follow has already been stored and answered, and no failure here SHALL change it.

#### Scenario: Search history unreadable

- **WHEN** reading the Artist's SearchLog fails with an error other than NotFound
- **THEN** SearchNewConcertsOnFirstFollow fails, no search starts, and the announced follow is processed again

#### Scenario: Search fails

- **WHEN** the Artist has never been searched and SearchNewConcerts fails
- **THEN** SearchNewConcertsOnFirstFollow fails and the announced follow is processed again
