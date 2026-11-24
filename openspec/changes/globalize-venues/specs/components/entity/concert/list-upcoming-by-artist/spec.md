## MODIFIED Requirements

### Requirement: Upcoming concerts of one artist, oldest first

ListUpcomingByArtist SHALL take an Artist and the current time, and SHALL return every Concert whose performers include the Artist and whose local date is on or after the current date at its Venue at that time, the date in the Venue's own time zone (see Venue), ordered by local date ascending, each with its Venue (name, admin area and time zone), Series and performers. Concerts that are not visible to fans (see Concert) SHALL be left out. An Artist with no upcoming concerts, or an unknown Artist, SHALL yield an empty list.

#### Scenario: Past concert left out
- **WHEN** the Artist performs on a past date and a future date
- **THEN** only the future Concert is returned

#### Scenario: Concert today
- **WHEN** the Artist performs today
- **THEN** that Concert is returned

#### Scenario: Yesterday's concert early in the morning
- **WHEN** the current time is 2026-11-10 23:30 UTC, which is 2026-11-11 at a Venue in Asia/Tokyo, and the Artist performed there on 2026-11-10
- **THEN** that Concert is not returned

#### Scenario: Today's concert in another time zone
- **WHEN** the current time is 2026-11-10 23:30 UTC, which is still 2026-11-10 at a Venue in America/New_York, and the Artist performs there on 2026-11-10
- **THEN** that Concert is returned

#### Scenario: Venue's time zone returned
- **WHEN** the Artist performs at a future date at a Venue in Asia/Taipei
- **THEN** the Concert is returned with its Venue's name, admin area and the time zone Asia/Taipei

#### Scenario: Draft Organizer concert excluded
- **WHEN** the Artist performs at a future DRAFT Event of a first-party Series
- **THEN** that Concert is not returned

#### Scenario: No upcoming concerts
- **WHEN** the Artist performs only on past dates
- **THEN** ListUpcomingByArtist returns an empty list
