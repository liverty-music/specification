# Search New Concerts

## Purpose

SearchNewConcerts searches external sources for one Artist's newly announced concerts, keeps only those not already in the catalog or pending review, announces them as a discovery for that Artist, and returns them as previews. It serves any caller, and a daily schedule runs it for every followed Artist.

## Requirements

### Requirement: Daily run over followed artists

Every day at 18:00 JST, SearchNewConcerts SHALL be run for each Artist that at least one User follows, one Artist at a time. A failure for one Artist SHALL NOT stop the run, but the run SHALL stop after 3 consecutive Artists fail; a success SHALL reset that count.

#### Scenario: Isolated failure
- **WHEN** the search fails for one Artist and succeeds for the next
- **THEN** the run continues through the remaining Artists

#### Scenario: Three failures in a row
- **WHEN** the search fails for 3 consecutive Artists
- **THEN** the run stops without searching the remaining Artists

### Requirement: Organizer-managed artists are not searched

SearchNewConcerts SHALL return no concerts, and SHALL perform no external search, when the Artist is represented by an active Organizer. When that check itself fails, the search SHALL proceed. When the Artist is no longer represented, it SHALL be searched again.

#### Scenario: Represented artist
- **WHEN** the Artist is represented by an active Organizer
- **THEN** no external search is performed and no concerts are returned

#### Scenario: Representation check unavailable
- **WHEN** the representation check fails
- **THEN** the search proceeds as for an unrepresented Artist

### Requirement: Skip when recently searched or discovered

Before searching, SearchNewConcerts SHALL read the Artist's SearchLog and return no concerts, performing no external search, when the SearchLog is fresh (freshness window 24 hours by default, configurable per environment), recently discovered (discovery window 14 days by default), or in progress (pending timeout 3 minutes). An Artist never searched, or whose last search failed and found nothing recently, SHALL be searched.

#### Scenario: Searched 2 hours ago
- **WHEN** the Artist's last search completed 2 hours ago
- **THEN** no external search is performed and no concerts are returned

#### Scenario: New concert found 3 days ago
- **WHEN** the last search completed 30 hours ago and found a new concert 3 days ago
- **THEN** no external search is performed

#### Scenario: Another search running
- **WHEN** a search for the Artist started 1 minute ago and is still pending
- **THEN** no external search is performed

#### Scenario: Previous search failed
- **WHEN** the last search failed 1 minute ago and nothing was found in the last 14 days
- **THEN** the external search is performed

### Requirement: The search is recorded

Before the external search, SearchNewConcerts SHALL restart the Artist's SearchLog as pending (SearchLog.Upsert), and SHALL fail without searching when that cannot be recorded. When the search ends with an error the status SHALL become failed; otherwise completed. When new concerts are announced, SearchNewConcerts SHALL record the discovery (SearchLog.MarkFound); a failure to update the status or record the discovery SHALL NOT change the result.

#### Scenario: Productive search
- **WHEN** the search announces two new concerts
- **THEN** the SearchLog is completed and its last found time is now

#### Scenario: Nothing new
- **WHEN** the search finds only known concerts
- **THEN** the SearchLog is completed and its last found time is unchanged

#### Scenario: External search fails
- **WHEN** the external search fails with an error
- **THEN** the SearchLog is failed and SearchNewConcerts fails

### Requirement: Artist data required

SearchNewConcerts SHALL fail with Internal, before any external search, when the Artist has no name or no MBID. A missing official site SHALL NOT prevent the search.

#### Scenario: Artist without MBID
- **WHEN** the Artist has no MBID
- **THEN** SearchNewConcerts fails with Internal and no external search is performed

### Requirement: Only new concerts are kept

SearchNewConcerts SHALL search from the current date (Concert.Search), then drop events already known among the Artist's upcoming Concerts (DiscoveredSeries.FilterNewSeries over Concert.ListByArtist upcoming only), then drop every event whose local date and normalized listed venue name match one of the Artist's pending StagedConcerts, whatever its start time. A series left with no events SHALL be dropped. The RejectedConcertLog and SuppressedConcerts SHALL NOT be consulted here.

#### Scenario: Already in the catalog
- **WHEN** a found event matches an upcoming Concert of the Artist
- **THEN** it is not announced

#### Scenario: Pending review at another start time
- **WHEN** a found event starts at 18:00 and a StagedConcert for the Artist is pending at the same date and venue starting 13:00
- **THEN** the event is not announced and the StagedConcert is not refreshed

#### Scenario: Previously rejected
- **WHEN** a found event matches only a RejectedConcertLog entry
- **THEN** it is announced

### Requirement: New concerts are announced once per search

When at least one event remains, SearchNewConcerts SHALL announce one discovery for the Artist carrying all remaining series, and SHALL fail when the announcement cannot be made. When none remains, it SHALL announce nothing and return no concerts without error.

#### Scenario: Two series found
- **WHEN** a tour and a standalone show remain
- **THEN** one discovery carrying both is announced

#### Scenario: Nothing new
- **WHEN** no event remains
- **THEN** nothing is announced and an empty list is returned

### Requirement: Returned previews

SearchNewConcerts SHALL return each announced event as a Concert preview with the Artist as its only performer and its series' title, type and source page. A preview SHALL have no event id and no Venue, and the events of one series SHALL share one preview series id that refers to no stored Series.

#### Scenario: Tour preview
- **WHEN** a tour with two new events is announced
- **THEN** two previews are returned sharing one series id and neither has a Venue
