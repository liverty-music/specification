# Concert.ListByArtist

## Purpose

Lists the Concerts at which one Artist performs, optionally only those from today onward, each with its Venue, Series and performers.

## Requirements

### Requirement: Concerts of one artist, oldest first

ListByArtist SHALL return every Concert whose performers include the Artist, ordered by local date ascending, each with its Venue (name and admin area), Series and performers. When asked for upcoming concerts only, it SHALL return only Concerts dated on or after the current date. Concerts of a Series that is not publicly visible SHALL be left out. An Artist with no concerts, or an unknown Artist, SHALL yield an empty list.

#### Scenario: Past and upcoming
- **WHEN** the Artist performs on a past date and a future date and all concerts are asked for
- **THEN** both Concerts are returned, the past one first

#### Scenario: Upcoming only
- **WHEN** the same Artist is listed with upcoming only
- **THEN** only the future Concert is returned

#### Scenario: Draft organizer concert excluded
- **WHEN** the Artist performs in a DRAFT first-party Series
- **THEN** that Concert is not returned

#### Scenario: No concerts
- **WHEN** the Artist performs in no Concert
- **THEN** ListByArtist returns an empty list

### Requirement: Empty artist is invalid

ListByArtist SHALL fail with InvalidArgument when the Artist is not given.

#### Scenario: Missing artist
- **WHEN** ListByArtist is called with no Artist
- **THEN** it fails with InvalidArgument
