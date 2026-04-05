### Requirement: URL-driven artist filter
The dashboard SHALL accept an `artists` query parameter containing one or more artist IDs (comma-separated UUIDs). When present, only concerts belonging to the listed artists SHALL be displayed. When absent or empty, all followed-artist concerts SHALL be displayed as normal.

#### Scenario: Single artist filter from URL
- **WHEN** the user navigates to `/dashboard?artists=<artistId>`
- **THEN** only concerts whose `artistId` matches `<artistId>` SHALL be shown in the concert highway

#### Scenario: Multiple artist filter from URL
- **WHEN** the user navigates to `/dashboard?artists=<id1>,<id2>`
- **THEN** only concerts whose `artistId` is in `{id1, id2}` SHALL be shown in the concert highway

#### Scenario: No filter — unfiltered view preserved
- **WHEN** the user navigates to `/dashboard` (no `artists` param)
- **THEN** all followed-artist concerts SHALL be displayed unchanged

#### Scenario: Unknown artist ID in filter
- **WHEN** an `artists` value contains an ID that does not match any followed artist
- **THEN** that ID SHALL be silently ignored; concerts for remaining valid IDs SHALL still be shown

#### Scenario: Filter yields empty result
- **WHEN** the filtered artist set has no upcoming concerts
- **THEN** the empty-state placeholder SHALL be displayed (same as the no-concerts state)

### Requirement: Filter state synchronised with URL
When the user changes the active filter via the UI, the dashboard URL SHALL be updated to reflect the new filter state without triggering a full page reload.

#### Scenario: User adds an artist to the filter
- **WHEN** the user selects an artist in the filter bottom sheet and confirms
- **THEN** the browser URL SHALL update to `/dashboard?artists=<selectedIds>` via `history.replaceState`
- **THEN** the concert highway SHALL immediately display only matching concerts

#### Scenario: Page reload preserves filter
- **WHEN** the user reloads the page while a filter is active
- **THEN** the `artists` query param SHALL be re-parsed from the URL
- **THEN** the same filtered view SHALL be restored

### Requirement: Filter chip UI in page header
The page header SHALL display a filter trigger button that visually indicates when a filter is active. Artist names SHALL NOT be rendered as chips in the header.

#### Scenario: No active filter — header unchanged
- **WHEN** `filteredArtistIds` is empty
- **THEN** no filter indicator SHALL be visible in the header beyond the compact filter trigger button
- **AND** the filter trigger button SHALL be in its default (inactive) visual state

#### Scenario: Active filter — icon state only
- **WHEN** `filteredArtistIds` contains one or more IDs
- **THEN** the filter trigger button SHALL display in its active visual state (e.g., color change via `[data-active="true"]` CSS)
- **AND** no artist name chips SHALL be rendered in the header

#### Scenario: Dismissing an active filter
- **WHEN** a filter is active and the user taps the filter trigger button
- **THEN** the bottom sheet SHALL open with currently filtered artists pre-selected
- **AND** the user can deselect artists and confirm to reduce or clear the filter

### Requirement: Artist-selection bottom sheet
A bottom sheet SHALL allow the user to select one or more followed artists as a filter.

#### Scenario: Opening the bottom sheet
- **WHEN** the user taps the filter trigger button
- **THEN** the bottom sheet SHALL open listing all followed artists

#### Scenario: Pre-selecting current filter
- **WHEN** the bottom sheet opens while a filter is already active
- **THEN** the currently filtered artists SHALL be pre-selected in the list

#### Scenario: Confirming selection
- **WHEN** the user selects artists and taps the confirm button
- **THEN** `filteredArtistIds` SHALL be updated to the selected set
- **THEN** the bottom sheet SHALL close

#### Scenario: Confirming empty selection
- **WHEN** the user deselects all artists and confirms
- **THEN** the filter SHALL be cleared (equivalent to no filter)

### Requirement: Push notification deep-link to filtered dashboard
Tapping a push notification that carries a `/dashboard?artists=<artistId>` URL SHALL open the dashboard pre-filtered to that artist.

#### Scenario: Notification tap opens filtered dashboard
- **WHEN** a push notification with `data.url = "/dashboard?artists=<artistId>"` is tapped
- **THEN** the browser SHALL navigate to `/dashboard?artists=<artistId>`
- **THEN** the dashboard SHALL display only concerts for `<artistId>`

#### Scenario: Filter disabled during onboarding
- **WHEN** the user is in the onboarding flow (lane intro active)
- **THEN** the filter trigger button SHALL be hidden or disabled
- **THEN** the `artists` query param SHALL be ignored until onboarding is complete
