## MODIFIED Requirements

### Requirement: Dashboard Mode Toggle

The Dashboard SHALL provide a segment toggle control that switches between "My Timetable" mode (current behavior — concerts for followed artists) and "All Nearby" mode (new — all concerts in the DB near a given location within a date range). The toggle is what tells the fan which mode is active: the page header title SHALL remain the dashboard's title in both modes.

#### Scenario: Default mode is My Timetable

- **WHEN** the Dashboard loads or the page is reloaded
- **THEN** the active mode SHALL default to "My Timetable"
- **AND** the toggle SHALL visually indicate My Timetable as the selected mode

#### Scenario: Mode-specific filters appear only in All Nearby

- **WHEN** the user switches to "All Nearby" mode
- **THEN** a date-preset selector and an area selector SHALL appear below the toggle
- **WHEN** the user switches back to "My Timetable" mode
- **THEN** the date-preset selector and area selector SHALL be hidden

#### Scenario: Switching modes replaces the concert list

- **WHEN** the user switches from My Timetable to All Nearby
- **THEN** the Dashboard SHALL call `ConcertService.ListByLocation` with the current location and date range
- **AND** the resulting `ProximityGroup[]` SHALL replace the concert list
- **WHEN** the user switches back to My Timetable
- **THEN** the Dashboard SHALL revert to the cached `ListByFollower` / `ListByArtists` result

#### Scenario: Header title does not change with the mode

- **WHEN** the user switches between My Timetable and All Nearby
- **THEN** the page header title SHALL stay the dashboard's title
- **AND** the toggle SHALL indicate the newly selected mode

### Requirement: Natural Japanese Copy for All Nearby

All user-facing Japanese strings on the All Nearby surface SHALL read as natural, native Japanese; machine-translated or awkward phrasing SHALL be corrected. Japanese and English i18n keys SHALL remain at parity.

#### Scenario: All Nearby strings are natural Japanese

- **WHEN** the mode toggle labels, area prompt, empty-state text, date-preset labels, and range hint are displayed in Japanese
- **THEN** each SHALL be phrased in natural Japanese
- **AND** every `allNearby.*` key present in the Japanese bundle SHALL also exist in the English bundle (and vice versa)
