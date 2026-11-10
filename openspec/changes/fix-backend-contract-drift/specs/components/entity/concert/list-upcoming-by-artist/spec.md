## Purpose

Lists the Concerts at which one Artist performs from the current date onward, each with its Venue, Series and performers, for the work that compares newly found concerts and sales against what is still to come.

## ADDED Requirements

### Requirement: Upcoming concerts of one artist, oldest first

ListUpcomingByArtist SHALL return every Concert whose performers include the Artist and whose local date is on or after the current date, ordered by local date ascending, each with its Venue (name and admin area), Series and performers. Concerts that are not visible to fans (see Concert) SHALL be left out. An Artist with no upcoming concerts, or an unknown Artist, SHALL yield an empty list.

#### Scenario: Past concert left out
- **WHEN** the Artist performs on a past date and a future date
- **THEN** only the future Concert is returned

#### Scenario: Concert today
- **WHEN** the Artist performs today
- **THEN** that Concert is returned

#### Scenario: Draft Organizer concert excluded
- **WHEN** the Artist performs at a future DRAFT Event of a first-party Series
- **THEN** that Concert is not returned

#### Scenario: No upcoming concerts
- **WHEN** the Artist performs only on past dates
- **THEN** ListUpcomingByArtist returns an empty list

### Requirement: Empty artist is invalid for upcoming concerts

ListUpcomingByArtist SHALL fail with InvalidArgument when the Artist is not given.

#### Scenario: Missing artist
- **WHEN** ListUpcomingByArtist is called with no Artist
- **THEN** it fails with InvalidArgument
