## ADDED Requirements

### Requirement: New concerts are handed on once per search

When at least one event remains, SearchNewConcerts SHALL start ConcertCreationUseCase.CreateFromDiscovered for the Artist with all remaining series, named after the Artist and the search time of its ConcertSearch, so this search starts it once. When it cannot be started, SearchNewConcerts SHALL fail. When none remains, it SHALL start nothing and return no concerts without error.

#### Scenario: Two series found
- **WHEN** a tour and a standalone show remain
- **THEN** CreateFromDiscovered is started once with both

#### Scenario: Nothing new
- **WHEN** no event remains
- **THEN** nothing is started and an empty list is returned

#### Scenario: Cannot be started
- **WHEN** two series remain and CreateFromDiscovered cannot be started
- **THEN** SearchNewConcerts fails and the ConcertSearch is failed

## MODIFIED Requirements

### Requirement: The search is recorded

Before the external search, SearchNewConcerts SHALL restart the Artist's ConcertSearch as pending (ConcertSearch.Upsert), and SHALL fail without searching when that cannot be recorded. When the search ends with an error the status SHALL become failed; otherwise completed. When new concerts are handed on, SearchNewConcerts SHALL record the discovery (ConcertSearch.MarkFound); a failure to update the status or record the discovery SHALL NOT change the result.

#### Scenario: Productive search
- **WHEN** the search hands on two new concerts
- **THEN** the ConcertSearch is completed and its last found time is now

#### Scenario: Nothing new
- **WHEN** the search finds only known concerts
- **THEN** the ConcertSearch is completed and its last found time is unchanged

#### Scenario: External search fails
- **WHEN** the external search fails with an error
- **THEN** the ConcertSearch is failed and SearchNewConcerts fails

### Requirement: Only new concerts are kept

SearchNewConcerts SHALL search from the current date (Concert.Search), then drop events already known among the Artist's upcoming Concerts (DiscoveredSeries.FilterNewSeries over Concert.ListByArtist upcoming only), then drop every event whose local date and normalized listed venue name match one of the Artist's pending ConcertCandidates, whatever its start time. A series left with no events SHALL be dropped. The RejectedConcert and SuppressedConcerts SHALL NOT be consulted here.

#### Scenario: Already in the catalog
- **WHEN** a found event matches an upcoming Concert of the Artist
- **THEN** it is not handed on

#### Scenario: Pending review at another start time
- **WHEN** a found event starts at 18:00 and a ConcertCandidate for the Artist is pending at the same date and venue starting 13:00
- **THEN** the event is not handed on and the ConcertCandidate is not refreshed

#### Scenario: Previously rejected
- **WHEN** a found event matches only a RejectedConcert entry
- **THEN** it is handed on

### Requirement: Returned previews

SearchNewConcerts SHALL return each event it hands on as a Concert preview with the Artist as its only performer and its series' title, type and source page. A preview SHALL have no event id and no Venue, and the events of one series SHALL share one preview series id that refers to no stored Series.

#### Scenario: Tour preview
- **WHEN** a tour with two new events is handed on
- **THEN** two previews are returned sharing one series id and neither has a Venue

### Requirement: Each search reports its outcome

Every run of SearchNewConcerts that performs the external search SHALL send one "concert search completed" signal for product analytics, under the trace of that search, carrying the Artist, what started it (the daily run, a first follow, or by hand), the outcome (failed, nothing new, or new concerts found) and the numbers of series and events it handed on. A failed search SHALL also carry the kind of error that failed it (such as deadline exceeded, unavailable or permission denied), or unknown when the error states no kind, and SHALL NOT carry the error's message. A run that returns before the external search sends no signal. A failure to send it SHALL NOT change the outcome.

#### Scenario: Nothing new
- **WHEN** the daily run searches an Artist and every event found is already known
- **THEN** one signal is sent with the outcome nothing new and 0 handed-on events

#### Scenario: Search failed
- **WHEN** the external search fails because the caller's deadline passed
- **THEN** one signal is sent with the outcome failed and the error kind deadline exceeded, and without the error's message

#### Scenario: Failure without a kind
- **WHEN** the external search fails with an error that states no kind
- **THEN** one signal is sent with the outcome failed and the error kind unknown

## REMOVED Requirements

### Requirement: New concerts are announced once per search
**Reason**: Found concerts are an observation handed to one receiver, not a fact other parts react to: SearchNewConcerts starts ConcertCreationUseCase.CreateFromDiscovered directly instead of announcing a discovery.
**Migration**: Replaced by "New concerts are handed on once per search". The behavior is the same: one hand-over per search carrying every remaining series, and a failure fails the search.
