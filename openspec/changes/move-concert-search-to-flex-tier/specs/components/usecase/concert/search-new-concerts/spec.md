## ADDED Requirements

### Requirement: The search runs in the background

After recording the ConcertSearch as pending, SearchNewConcerts SHALL start the rest of the search (Concert.Search, the filtering, the hand-on, the status update and the completed signal) as a background workflow named after the Artist and the search time of its ConcertSearch, and SHALL return without concerts and without waiting for it. Starting it again with the same Artist and search time SHALL NOT start a second search. When it cannot be started, SearchNewConcerts SHALL fail. At most 8 background searches SHALL run at once across all backend processes; the others wait for one to end. A step of the background search that fails with Unavailable or DeadlineExceeded SHALL be tried again as every workflow step is (first after 1 second, then at doubling intervals of at most 1 hour), until 20 hours after the search time, when the background search stops and is reported for an admin as a workflow past its deadline.

#### Scenario: Daily run starts searches and ends
- **WHEN** the daily run reaches 80 followed Artists that are due for a search
- **THEN** each of them has a pending ConcertSearch and a started background search, and the run ends without waiting for any of them

#### Scenario: Eight at once
- **WHEN** 20 background searches have been started and none has ended
- **THEN** 8 of them are searching and 12 are waiting

#### Scenario: Same search started twice
- **WHEN** the background search for an Artist and a search time is started twice
- **THEN** the external search runs once for it

#### Scenario: Service busy for 3 hours
- **WHEN** Concert.Search fails with Unavailable for the first 3 hours after the search time and then succeeds
- **THEN** the background search continues from that result, the ConcertSearch becomes completed, and nothing is reported for an admin

#### Scenario: Service busy for a whole day
- **WHEN** Concert.Search still fails with Unavailable 20 hours after the search time
- **THEN** the background search stops, it is reported for an admin, and the ConcertSearch stays pending

#### Scenario: Cannot be started
- **WHEN** the ConcertSearch is recorded as pending and the background search cannot be started
- **THEN** SearchNewConcerts fails

## MODIFIED Requirements

### Requirement: Skip when recently searched or discovered

Before searching, SearchNewConcerts SHALL read the Artist's ConcertSearch and return no concerts, performing no external search, when the ConcertSearch is fresh (freshness window 24 hours by default, configurable per environment), recently discovered (discovery window 14 days by default), or in progress (pending timeout 20 hours, the time a background search may keep retrying). An Artist never searched, whose last search failed and found nothing recently, or whose pending search started 20 hours ago or earlier, SHALL be searched.

#### Scenario: Searched 2 hours ago
- **WHEN** the Artist's last search completed 2 hours ago
- **THEN** no external search is performed and no concerts are returned

#### Scenario: New concert found 3 days ago
- **WHEN** the last search completed 30 hours ago and found a new concert 3 days ago
- **THEN** no external search is performed

#### Scenario: Another search running
- **WHEN** a search for the Artist started 5 hours ago and is still pending
- **THEN** no external search is performed

#### Scenario: Abandoned search
- **WHEN** a search for the Artist started 21 hours ago, is still pending, and nothing was found in the last 14 days
- **THEN** the external search is performed

#### Scenario: Previous search failed
- **WHEN** the last search failed 1 minute ago and nothing was found in the last 14 days
- **THEN** the external search is performed

### Requirement: The search is recorded

Before starting the background search, SearchNewConcerts SHALL restart the Artist's ConcertSearch as pending (ConcertSearch.Upsert), and SHALL fail without searching when that cannot be recorded. When the background search ends with an error the status SHALL become failed; otherwise completed. When new concerts are handed on, the background search SHALL record the discovery (ConcertSearch.MarkFound); a failure to update the status or record the discovery SHALL NOT change the result. A background search stopped at its deadline SHALL leave the status pending.

#### Scenario: Productive search
- **WHEN** the background search hands on two new concerts
- **THEN** the ConcertSearch is completed and its last find time is the time of the hand-on

#### Scenario: Nothing new
- **WHEN** the background search finds only known concerts
- **THEN** the ConcertSearch is completed and its last find time is unchanged

#### Scenario: External search fails
- **WHEN** Concert.Search fails with a permanent error
- **THEN** the ConcertSearch is failed and the background search ends with that error

### Requirement: New concerts are handed on once per search

When at least one event remains, the background search SHALL start ConcertCreationUseCase.CreateFromDiscovered for the Artist with all remaining series, named after the Artist and the search time of its ConcertSearch, so this search starts it once. When it cannot be started, the background search SHALL fail. When none remains, it SHALL start nothing.

#### Scenario: Two series found
- **WHEN** a tour and a standalone show remain
- **THEN** CreateFromDiscovered is started once with both

#### Scenario: Nothing new
- **WHEN** no event remains
- **THEN** nothing is started and the ConcertSearch is completed

#### Scenario: Cannot be started
- **WHEN** two series remain and CreateFromDiscovered cannot be started with a permanent error
- **THEN** the background search fails and the ConcertSearch is failed

## REMOVED Requirements

### Requirement: Returned previews
**Reason**: SearchNewConcerts returns before the search has run, so it has nothing to preview; no caller read the previews (the daily run and SearchNewConcertsOnFirstFollow discarded them).
**Migration**: None. The concerts reach the catalog through CreateFromDiscovered as before.
