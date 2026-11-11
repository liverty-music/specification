# Concert.ListByArtist

## Purpose

Lists the Concerts at which one Artist performs, of every date, each with its Venue, Series and performers.

## Requirements

### Requirement: Empty artist is invalid

ListByArtist SHALL fail with InvalidArgument when the Artist is not given.

#### Scenario: Missing artist
- **WHEN** ListByArtist is called with no Artist
- **THEN** it fails with InvalidArgument

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
