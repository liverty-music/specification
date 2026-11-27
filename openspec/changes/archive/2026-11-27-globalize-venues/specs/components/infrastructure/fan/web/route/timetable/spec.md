## MODIFIED Requirements

### Requirement: Default today-onward timetable

The timetable "My Timetable" SHALL, by default, display only concerts on or after the current date at each concert's venue. For the default view the timetable SHALL call `ConcertService.ListFollowed` without the `from` argument, so the server applies each venue's own "today"; it SHALL NOT send the device's local date.

#### Scenario: Fresh load defaults to today onward

- **WHEN** the user opens `/timetable` with no date query parameter
- **THEN** the timetable SHALL request `ConcertService.ListFollowed` without `from`
- **AND** only concerts on or after today at their venue SHALL be displayed
- **AND** past concerts of followed artists SHALL NOT be displayed

#### Scenario: Concert abroad still today at its venue

- **WHEN** the user in Japan opens `/timetable` at 08:00 on 15 March, and a followed artist plays in London on 14 March, where it is still 14 March
- **THEN** that concert SHALL be displayed

#### Scenario: Empty upcoming timetable

- **WHEN** the default (today-onward) timetable contains no upcoming concerts for the user's followed artists
- **THEN** the empty-state placeholder SHALL be displayed
- **AND** the "過去のコンサートも表示" affordance SHALL remain available so the user can look back

### Requirement: Guest timetable follows the same date lower bound

The guest timetable SHALL show only the concert dates the signed-in timetable would show: on or after the active `from` date or, without one, on or after the current date at each concert's venue, both when it opens and after its resume refresh. Choosing an earlier date in the date filter SHALL show the earlier concerts again.

#### Scenario: Guest timetable hides past concerts

- **WHEN** a guest who follows artists with concerts before and after today opens `/timetable` with no date query parameter
- **THEN** only concerts on or after today at their venue SHALL be displayed
- **AND** past concerts of the followed artists SHALL NOT be displayed

#### Scenario: Guest's concert abroad still today at its venue

- **WHEN** a guest in Japan opens `/timetable` at 08:00 on 15 March, and a followed artist plays in London on 14 March, where it is still 14 March
- **THEN** that concert SHALL be displayed

#### Scenario: Guest looks back

- **WHEN** the guest chooses a date earlier than today in the date filter
- **THEN** the concerts on or after that date SHALL be displayed, without loading the list again when the guest has already loaded it

#### Scenario: Guest resume refresh keeps the cut

- **WHEN** a guest on `/timetable` returns the PWA to the foreground and the list is refreshed
- **THEN** only concerts on or after the timetable's lower bound SHALL be displayed
