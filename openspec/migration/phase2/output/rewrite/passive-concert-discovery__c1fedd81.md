<!-- spec: passive-concert-discovery | target: components/infrastructure/fan/web/route/dashboard | flags: CLASSNAME | new_name: Compact All Nearby Filter Bar -->

### Requirement: Compact All Nearby Filter Bar

The All Nearby mode SHALL present its filters as a single, fixed-height row of two chips — an area chip and a date chip — such that selecting or adjusting any filter never changes the height of the filter area and therefore never reduces the concert timetable's height.

#### Scenario: Filter bar is a single row of two chips

- **WHEN** All Nearby mode is active
- **THEN** the filter area SHALL render exactly two controls on one row: an area chip and a date chip
- **AND** neither chip SHALL expand the filter area inline when tapped

#### Scenario: Timetable height is unaffected by filter interaction

- **WHEN** the user opens the area sheet, opens the date sheet, or changes any filter
- **THEN** the height of the concert timetable SHALL NOT decrease as a result
- **AND** all complex input SHALL occur in a bottom sheet overlay rather than inline expansion
