## REMOVED Requirements

### Requirement: Concerts of one artist, oldest first

**Reason**: The option to list upcoming Concerts only is a second filter on one operation, which the backend's review rules make a separate operation.

**Migration**: Callers that asked for upcoming Concerts only call Concert.ListUpcomingByArtist; the rest call ListByArtist, which now lists Concerts of every date.

## ADDED Requirements

### Requirement: Concerts of one artist of every date, oldest first

ListByArtist SHALL return every Concert whose performers include the Artist, of every date, ordered by local date ascending, each with its Venue (name and admin area), Series and performers. Concert.ListUpcomingByArtist lists only the Concerts from the current date onward. Concerts that are not visible to fans (see Concert) SHALL be left out. An Artist with no concerts, or an unknown Artist, SHALL yield an empty list.

#### Scenario: Past and upcoming
- **WHEN** the Artist performs on a past date and a future date
- **THEN** both Concerts are returned, the past one first

#### Scenario: Draft Organizer concert excluded
- **WHEN** the Artist performs at a DRAFT Event of a first-party Series
- **THEN** that Concert is not returned

#### Scenario: No concerts
- **WHEN** the Artist performs in no Concert
- **THEN** ListByArtist returns an empty list

#### Scenario: Draft and cancelled dates of a published tour excluded
- **WHEN** the Artist performs in a PUBLIC Series with one PUBLISHED, one DRAFT and one CANCELLED Event
- **THEN** only the PUBLISHED Event's Concert is returned
