## ADDED Requirements

### Requirement: The search runs in the background

After recording the ConcertSearch as pending, SearchNewConcerts SHALL start the rest of the search (Concert.Search, the filtering, the hand-on, the status update and the completed signal) as a background search for the Artist and the search time of its ConcertSearch, and SHALL return without concerts and without waiting for it. When it cannot be started, SearchNewConcerts SHALL fail.

The background search SHALL call Concert.Search in attempts:
- Each attempt SHALL call Concert.Search once and SHALL run once, also when it is started again.
- When Concert.Search fails with Unavailable or DeadlineExceeded, the next attempt SHALL start after a wait of 1 minute for the first retry, doubling with each further retry up to at most 1 hour, provided that it would start less than 20 hours after the search time. Otherwise no further attempt SHALL start.
- At most 8 attempts SHALL be calling Concert.Search at once across all backend processes. Attempts waiting to retry SHALL NOT count toward those 8.
- No attempt SHALL call Concert.Search 20 hours or more after the search time. The search then SHALL end as failed (see "The search is recorded").

#### Scenario: Daily run starts searches and ends
- **WHEN** the daily run reaches 80 followed Artists that are due for a search
- **THEN** each of them has a pending ConcertSearch and a started background search, and the run ends without waiting for any of them

#### Scenario: Eight at once
- **WHEN** 20 background searches are ready to call Concert.Search and none has ended
- **THEN** 8 of them are calling it and 12 are waiting

#### Scenario: Waiting retries hold no place
- **WHEN** 8 background searches are waiting to retry after Unavailable and a ninth is ready to call Concert.Search
- **THEN** the ninth calls it without waiting for the 8

#### Scenario: Same attempt started twice
- **WHEN** the same attempt of a background search is started twice
- **THEN** Concert.Search is called once for it

#### Scenario: Service busy for 3 hours
- **WHEN** Concert.Search fails with Unavailable on every attempt in the first 3 hours after the search time and then succeeds
- **THEN** the search continues from that result, the ConcertSearch becomes completed, and one concert search completed signal is sent

#### Scenario: Queued until late
- **WHEN** an attempt is first able to call Concert.Search 20 hours and 5 minutes after the search time
- **THEN** it does not call Concert.Search and the search ends as failed

#### Scenario: Cannot be started
- **WHEN** the ConcertSearch is recorded as pending and the background search cannot be started
- **THEN** SearchNewConcerts fails

### Requirement: Each attempt checks again before searching

Before calling Concert.Search, every attempt of a background search SHALL read the Artist's ConcertSearch and the Artist again:
- When the ConcertSearch is no longer pending with the search's search time, the attempt SHALL end without calling Concert.Search and without changing the ConcertSearch.
- When the Artist's activity has ended or an active Organizer represents it, the attempt SHALL end without calling Concert.Search, and the ConcertSearch SHALL become completed without a find.
- When the representation check itself fails, the attempt SHALL proceed, as SearchNewConcerts does.
- When there is no ConcertSearch, the attempt SHALL end as for a replaced one. When either read fails otherwise, it SHALL be tried again if the failure is Unavailable or DeadlineExceeded; any other failure SHALL fail the background search itself, leaving the ConcertSearch unchanged, for an admin to resolve.

#### Scenario: Represented while waiting
- **WHEN** an active Organizer comes to represent the Artist while its search waits to retry
- **THEN** the next attempt does not call Concert.Search and the ConcertSearch is completed

#### Scenario: Search replaced
- **WHEN** an attempt starts and the Artist's ConcertSearch has a later search time than the attempt's
- **THEN** the attempt does not call Concert.Search and the ConcertSearch is unchanged

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

Before starting the background search, SearchNewConcerts SHALL restart the Artist's ConcertSearch as pending (ConcertSearch.Upsert), and SHALL fail without searching when that cannot be recorded. The background search SHALL set the status when it ends:
- **failed** when Concert.Search, or a read an attempt makes between the check and that call, fails with an error other than Unavailable or DeadlineExceeded; when CreateFromDiscovered cannot be started; or when no further attempt may call Concert.Search within 20 hours of the search time because it is still failing with Unavailable or DeadlineExceeded or has not been called yet;
- **completed** otherwise.

When a later search has replaced the Artist's ConcertSearch by the time the background search ends, it SHALL leave the status unchanged. When new concerts are handed on, the background search SHALL record the discovery (ConcertSearch.MarkFound). A transient failure (Unavailable or DeadlineExceeded) to update the status SHALL be tried again until the status is written, because a ConcertSearch left pending keeps the Artist from being searched. A failure to update the status or record the discovery SHALL NOT change the result.

#### Scenario: Productive search
- **WHEN** the background search hands on two new concerts
- **THEN** the ConcertSearch is completed and its last find time is the time of the hand-on

#### Scenario: Nothing new
- **WHEN** the background search finds only known concerts
- **THEN** the ConcertSearch is completed and its last find time is unchanged

#### Scenario: External search fails
- **WHEN** Concert.Search fails with a permanent error
- **THEN** the ConcertSearch is failed and no further attempt starts

#### Scenario: Status write fails for a moment
- **WHEN** a background search ends and the status update fails with Unavailable once
- **THEN** the update is tried again, and one concert search completed signal is sent

#### Scenario: Replaced while the last call ran
- **WHEN** a later search of the Artist is recorded while an earlier search's last call to Concert.Search is running
- **THEN** the earlier search leaves the ConcertSearch status unchanged and still reports its outcome

#### Scenario: Service busy for a whole day
- **WHEN** Concert.Search still fails with Unavailable on the last attempt it may make within 20 hours of the search time
- **THEN** the ConcertSearch is failed and no further attempt starts

### Requirement: New concerts are handed on once per search

When at least one event remains, the background search SHALL start ConcertCreationUseCase.CreateFromDiscovered for the Artist with all remaining series, named after the Artist and the search time of its ConcertSearch, so this search starts it once. When it cannot be started, the background search SHALL end as failed. When none remains, it SHALL start nothing.

#### Scenario: Two series found
- **WHEN** a tour and a standalone show remain
- **THEN** CreateFromDiscovered is started once with both

#### Scenario: Nothing new
- **WHEN** no event remains
- **THEN** nothing is started and the ConcertSearch is completed

#### Scenario: Cannot be started
- **WHEN** two series remain and CreateFromDiscovered cannot be started
- **THEN** the background search ends as failed and the ConcertSearch is failed

### Requirement: Each search reports its outcome

Every background search that calls Concert.Search SHALL send one "concert search completed" signal for product analytics when it ends, under the trace of that search. The signal SHALL carry:
- the Artist;
- what started it (the daily run, a first follow, or by hand);
- the outcome (failed, nothing new, or new concerts found);
- the numbers of series and events it handed on.

A failed search SHALL also carry the kind of error that failed it, or unknown when the error states no kind, and SHALL NOT carry the error's message. Examples of an error kind are deadline exceeded, unavailable and permission denied. A search that ended because no further attempt could start within 20 hours of the search time SHALL carry the kind of the error its last call returned.

Retried attempts SHALL NOT send a signal of their own. A search that finds itself replaced when an attempt starts sends no signal, also when an earlier attempt called Concert.Search. A search that ends before any call to Concert.Search sends no signal, including a search whose first attempt could only start 20 hours or more after the search time. A failure to send the signal SHALL NOT change the outcome.

#### Scenario: Nothing new
- **WHEN** the daily run searches an Artist and every event found is already known
- **THEN** one signal is sent with the outcome nothing new and 0 handed-on events

#### Scenario: Search failed
- **WHEN** Concert.Search fails because its deadline passed and no further attempt may be made within 20 hours of the search time
- **THEN** one signal is sent with the outcome failed and the error kind deadline exceeded, and without the error's message

#### Scenario: Failure without a kind
- **WHEN** Concert.Search fails permanently with an error that states no kind
- **THEN** one signal is sent with the outcome failed and the error kind unknown

#### Scenario: Busy for a whole day
- **WHEN** every attempt of a search failed with Unavailable until no further attempt could start within 20 hours of the search time
- **THEN** exactly one signal is sent, with the outcome failed and the error kind unavailable

## REMOVED Requirements

### Requirement: Returned previews
**Reason**: SearchNewConcerts returns before the search has run, so it has nothing to preview; no caller read the previews (the daily run and SearchNewConcertsOnFirstFollow discarded them).
**Migration**: None. The concerts reach the catalog through CreateFromDiscovered as before.
