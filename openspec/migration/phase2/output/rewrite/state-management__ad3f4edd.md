<!-- spec: state-management | target: components/usecase/concert/search-new-concerts | flags: CLASSNAME | new_name: Search and track new concerts for followed artists -->

### Requirement: Search and track new concerts for followed artists

The `ConcertServiceClient` singleton SHALL provide a `searchAndTrack(artistId, signal, targetCount, onConcertFound?)` method that encapsulates the full search lifecycle: initiate backend search, poll for completion, verify concerts on completion, and accumulate results in `artistsWithConcerts`. The service SHALL own an observable set of artist IDs (`artistsWithConcerts`) tracking which artists have confirmed concerts.

#### Scenario: searchAndTrack initiates backend search

- **WHEN** `searchAndTrack(artistId)` is called
- **AND** the artist is not already tracked
- **THEN** the system SHALL call `searchNewConcerts(artistId)` fire-and-forget
- **AND** the system SHALL start polling via `setInterval` (2000ms) if not already running

#### Scenario: searchAndTrack for already-tracked artist is no-op

- **WHEN** `searchAndTrack(artistId)` is called for an artist already in the tracking map
- **THEN** the system SHALL NOT initiate a new search or duplicate the tracking entry

#### Scenario: Poll detects search completion

- **WHEN** `listSearchStatuses` returns `completed` for an artist
- **THEN** the system SHALL call `listConcerts(artistId)`
- **AND** if concerts exist, the system SHALL add `artistId` to `artistsWithConcerts`
- **AND** if an `onConcertFound` callback was provided, the system SHALL invoke it with the artist ID

#### Scenario: Poll detects search failure

- **WHEN** `listSearchStatuses` returns `failed` for an artist
- **THEN** the system SHALL mark the artist as done without checking concerts

#### Scenario: Per-artist timeout

- **WHEN** an artist's search has been pending for >= 15 seconds
- **THEN** the system SHALL mark the artist as done (timeout)

#### Scenario: Early polling stop at target

- **WHEN** `artistsWithConcerts.size` reaches the provided target count
- **THEN** the system SHALL stop polling immediately via `clearInterval`

#### Scenario: All searches complete stops polling

- **WHEN** all tracked artists have status `done`
- **AND** `artistsWithConcerts.size` has not yet reached the target
- **THEN** the system SHALL stop polling

#### Scenario: AbortSignal cancels polling

- **WHEN** the provided `AbortSignal` is aborted (e.g., page navigation)
- **THEN** the system SHALL stop polling via `clearInterval`
- **AND** the system SHALL retain `artistsWithConcerts` state (not clear it)

#### Scenario: artistsWithConcertsCount getter

- **WHEN** `artistsWithConcertsCount` is accessed
- **THEN** it SHALL return `artistsWithConcerts.size`
