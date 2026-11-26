## ADDED Requirements

### Requirement: Guest timetable follows the same date lower bound

The guest timetable SHALL show only the concert dates on or after the timetable's active `from` date (today by default), the same lower bound the signed-in timetable shows. Where the default view of the signed-in timetable stops sending a device date (`globalize-venues`), the guest default bound is not defined by this requirement: that change must define the guest read's own Venue-local bound. The guest list is read with `ConcertService.ListByArtists`, which has no `from` and returns past and upcoming concerts, so the client SHALL cut the result to dates on or after `from` for the guest timetable and its resume refresh. The cut SHALL NOT change what `ListByArtists` returns to other callers or what the client caches, so choosing an earlier date in the date filter SHALL show the earlier concerts again.

#### Scenario: Guest timetable hides past concerts

- **WHEN** a guest who follows artists with concerts before and after today opens `/timetable` with no date query parameter
- **THEN** only concerts on or after the timetable's `from` date SHALL be displayed
- **AND** past concerts of the followed artists SHALL NOT be displayed

#### Scenario: Guest looks back

- **WHEN** the guest chooses a date earlier than today in the date filter
- **THEN** the concerts on or after that date SHALL be displayed, without a second `ListByArtists` call when the list is cached

#### Scenario: Guest resume refresh keeps the cut

- **WHEN** a guest on `/timetable` returns the PWA to the foreground and the list is refreshed
- **THEN** only concerts on or after the timetable's `from` date SHALL be displayed
