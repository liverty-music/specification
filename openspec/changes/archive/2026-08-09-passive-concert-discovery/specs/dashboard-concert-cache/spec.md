## ADDED Requirements

### Requirement: All Nearby mode uses ListByLocation

The Dashboard concert cache SHALL support an "All Nearby" mode that calls `ConcertService.ListByLocation` and caches its result separately from the My Timetable result.

#### Scenario: All Nearby result cached independently

- **WHEN** the user switches to All Nearby mode and `ListByLocation` returns a result
- **THEN** the result SHALL be stored in route-local state separate from the My Timetable cache
- **AND** switching back to My Timetable and then to All Nearby again SHALL reuse the cached All Nearby result if the location and date range have not changed

#### Scenario: Cache invalidated on filter change

- **WHEN** the user changes the area or date preset in All Nearby mode
- **THEN** the All Nearby cache SHALL be invalidated
- **AND** `ListByLocation` SHALL be called again with the new parameters

#### Scenario: My Timetable cache unaffected by All Nearby mode

- **WHEN** the user switches between My Timetable and All Nearby mode
- **THEN** the My Timetable concert cache SHALL remain intact
- **AND** switching back to My Timetable SHALL display the previously loaded result without an additional network call
