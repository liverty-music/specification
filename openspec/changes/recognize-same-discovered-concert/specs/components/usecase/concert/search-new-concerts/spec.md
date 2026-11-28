## MODIFIED Requirements

### Requirement: Only new concerts are kept

SearchNewConcerts SHALL search from the current time (Concert.Search, which leaves out events dated before the current date at their Venue), then drop events already known among the Artist's upcoming Concerts (DiscoveredSeries.FilterNewSeries over Concert.ListUpcomingByArtist at the same time), then drop every event that has the local date and the same listed venue (see Venue, "Same listed venue") of one of the Artist's pending ConcertCandidates, whatever its start time, then drop every event that is the same listing (see RejectedConcert, "Same listing") as one of the Artist's RejectedConcert entries (RejectedConcert.ListByArtist). A series left with no events SHALL be dropped.

#### Scenario: Already in the catalog
- **WHEN** a found event matches an upcoming Concert of the Artist
- **THEN** it is not handed on

#### Scenario: Pending review at another start time
- **WHEN** a found event starts at 18:00 and a ConcertCandidate for the Artist is pending at the same date and venue starting 13:00
- **THEN** the event is not handed on and the ConcertCandidate is not refreshed

#### Scenario: Previously rejected
- **WHEN** a found event is the same listing as one of the Artist's RejectedConcert entries
- **THEN** it is not handed on

#### Scenario: Rejected listing corrected
- **WHEN** a RejectedConcert entry of the Artist has no start time and a found event at its date and listed venue starts at 19:00
- **THEN** it is handed on
