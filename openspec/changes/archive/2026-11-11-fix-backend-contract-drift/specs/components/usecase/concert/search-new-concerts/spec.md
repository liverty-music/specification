## MODIFIED Requirements

### Requirement: Only new concerts are kept

SearchNewConcerts SHALL search from the current time (Concert.Search, which leaves out events dated before the current date at their Venue), then drop events already known among the Artist's upcoming Concerts (DiscoveredSeries.FilterNewSeries over Concert.ListUpcomingByArtist at the same time), then drop every event whose local date and normalized listed venue name match one of the Artist's pending ConcertCandidates, whatever its start time. A series left with no events SHALL be dropped. The RejectedConcert and SuppressedConcerts SHALL NOT be consulted here.

#### Scenario: Already in the catalog
- **WHEN** a found event matches an upcoming Concert of the Artist
- **THEN** it is not handed on

#### Scenario: Pending review at another start time
- **WHEN** a found event starts at 18:00 and a ConcertCandidate for the Artist is pending at the same date and venue starting 13:00
- **THEN** the event is not handed on and the ConcertCandidate is not refreshed

#### Scenario: Previously rejected
- **WHEN** a found event matches only a RejectedConcert entry
- **THEN** it is handed on
