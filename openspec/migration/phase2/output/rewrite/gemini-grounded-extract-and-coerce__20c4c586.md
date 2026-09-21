<!-- spec: gemini-grounded-extract-and-coerce | target: components/usecase/concert/search-new-concerts | flags: CLASSNAME | new_name: Discovered concert dates infer missing year from page context -->

### Requirement: Step 1 fills in missing years from page context for partial dates

When the source page emits a date without a year (e.g. `01.16. sat`, `8月7日`), Step 1 SHALL infer the year from page context — the tour title's year range, the page heading, surrounding chronological references — and prefix the verbatim raw value with that year. The emitted `<local_date>` SHALL therefore always carry a 4-digit year as its first token.

#### Scenario: Tour title spans two years and the date is in the second year

- **WHEN** Step 1 reads a page titled "TOUR 2026-2027" with an entry `01.16. sat` after a header listing earlier 2026 dates
- **THEN** the emitted `<local_date>` SHALL be `2027.01.16. sat`

#### Scenario: Tour title spans two years and the date is in the first year

- **WHEN** Step 1 reads the same "TOUR 2026-2027" page with an entry `08.01. sat` near the start of the schedule
- **THEN** the emitted `<local_date>` SHALL be `2026.08.01. sat`

#### Scenario: Source already provides the year

- **WHEN** the source page emits `2026年3月15日(土)` for an event
- **THEN** Step 1 SHALL emit `<local_date>2026年3月15日(土)</local_date>` verbatim with no year prepended
