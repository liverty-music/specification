# dashboard-date-filter Specification

## Purpose

Defines the dashboard timetable's date-based filtering: a URL-synchronised date query parameter, the collapsible date facet in the filter bottom sheet ("過去のコンサートも表示" → "この日付以降を表示"), the default today-onward view, and the past-inclusive re-fetch it triggers. Unlike the artist and journey facets, which narrow the already-loaded set client-side, the date facet changes what the server returns via a `ListByFollower` round-trip.

## Requirements

### Requirement: Default today-onward timetable

The dashboard "My Timetable" SHALL, by default, display only concerts whose date is on or after the current local date. The "today" boundary SHALL be anchored to the client's local date, and the dashboard SHALL request the timetable by passing that date as the `from` argument to `ListByFollower`.

#### Scenario: Fresh load defaults to today onward

- **WHEN** the user opens `/dashboard` with no date query parameter
- **THEN** the timetable SHALL request `ListByFollower` with `from` set to the client's current local date
- **AND** only concerts on or after today SHALL be displayed
- **AND** past concerts of followed artists SHALL NOT be displayed

#### Scenario: Empty upcoming timetable

- **WHEN** the default (today-onward) timetable contains no upcoming concerts for the user's followed artists
- **THEN** the empty-state placeholder SHALL be displayed
- **AND** the "過去のコンサートも表示" affordance SHALL remain available so the user can look back

### Requirement: URL-driven date filter

The dashboard SHALL accept a date query parameter (e.g. `from`) containing a single calendar date. When present, the timetable SHALL display concerts on or after that date, including past concerts when the date precedes today. When absent, the timetable SHALL behave as the default today-onward view.

#### Scenario: Past date from URL

- **WHEN** the user navigates to `/dashboard?from=<pastDate>`
- **THEN** the timetable SHALL request `ListByFollower` with `from = <pastDate>`
- **AND** concerts on or after `<pastDate>` (including past ones) SHALL be displayed

#### Scenario: Invalid or malformed date value

- **WHEN** the date query parameter is missing, empty, or not a valid calendar date
- **THEN** it SHALL be ignored and the default today-onward view SHALL be shown

#### Scenario: Future date from URL

- **WHEN** the date query parameter is a date after today
- **THEN** the timetable SHALL display only concerts on or after that future date

### Requirement: Date facet in the filter bottom sheet

The filter bottom sheet SHALL include a date facet presented as a collapsed affordance labelled "過去のコンサートも表示". Expanding it SHALL reveal a single date field labelled "この日付以降を表示" for choosing the earliest date to display. The facet SHALL coexist with the existing artist and journey facets in the same sheet and be committed by the same confirm action.

#### Scenario: Expanding the date facet

- **WHEN** the user taps "過去のコンサートも表示" in the filter bottom sheet
- **THEN** a single date field ("この日付以降を表示") SHALL be revealed
- **AND** the field SHALL default to the currently active `from` date (today when the default view is active)

#### Scenario: Choosing a past date and confirming

- **WHEN** the user picks a date earlier than today in the date field and taps confirm
- **THEN** the bottom sheet SHALL close
- **AND** the dashboard URL SHALL update to carry the chosen date without a full page reload
- **AND** the timetable SHALL re-fetch via `ListByFollower` with `from` set to the chosen date and display the past-inclusive result

#### Scenario: Collapsing back to today onward

- **WHEN** a past date is active and the user clears the date facet (returns it to the default) and confirms
- **THEN** the date query parameter SHALL be removed from the URL
- **AND** the timetable SHALL revert to the default today-onward view

#### Scenario: Date facet combines with artist and journey facets

- **WHEN** a past `from` date is active together with an artist and/or journey filter
- **THEN** the timetable SHALL first load all followed-artist concerts on or after `from`, then narrow that set by the active artist and journey facets
- **AND** the per-artist and journey chip counts SHALL be computed over the loaded (past-inclusive) set

### Requirement: Date filter state persistence

The active date filter SHALL survive a page reload and be shareable via the URL, consistent with the existing artist and journey filters.

#### Scenario: Reload preserves the date filter

- **WHEN** the user reloads the page while a past `from` date is active
- **THEN** the date query parameter SHALL be re-parsed from the URL
- **AND** the same past-inclusive timetable SHALL be restored
