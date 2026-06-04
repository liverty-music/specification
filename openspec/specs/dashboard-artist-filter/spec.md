# Dashboard Artist Filter

## Purpose

Defines the dashboard's artist-based filtering of the concert highway: a URL-synchronised `artists` query parameter, the filter chip UI in the page header, the artist-selection bottom sheet (count-prefixed, count-sorted chips), and guest availability of the filter.
## Requirements
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
A bottom sheet SHALL allow the user to select one or more followed artists as a filter. Artists SHALL be presented as pill-shaped chip elements. Each artist chip SHALL be prefixed with the number of that artist's upcoming concerts in the loaded dashboard set. The artist chips SHALL be ordered by that concert count descending (ties broken by artist name ascending), and artists with zero upcoming concerts SHALL NOT be listed. A "全て解除" (Clear all) button SHALL appear beside the sheet title and allow the user to deselect all pending selections across every facet in the sheet before confirming.

The sheet content SHALL be structured as a `<section>` element (not `<fieldset>`) with an `<h2>` heading as the title. The chip list SHALL carry `aria-labelledby` referencing the heading ID. `role="group"` SHALL NOT be applied to the `<ul>` element as it overrides the native `list` role and causes screen readers to lose item count information.

#### Scenario: Opening the bottom sheet
- **WHEN** the user taps the filter trigger button
- **THEN** the bottom sheet SHALL open listing the followed artists (that have upcoming concerts) as selectable chips

#### Scenario: Artist chip shows upcoming-concert count
- **WHEN** an artist chip is rendered
- **THEN** it SHALL display the count of that artist's upcoming concerts in the loaded dashboard set as a prefix to the artist name

#### Scenario: Chips ordered by concert count descending
- **WHEN** the artist chips are listed
- **THEN** they SHALL be ordered by upcoming-concert count descending
- **AND** ties SHALL be broken by artist name ascending

#### Scenario: Zero-concert artists hidden
- **WHEN** a followed artist has no upcoming concerts in the loaded dashboard set
- **THEN** that artist SHALL NOT appear in the chip list

#### Scenario: Counts stable while filtering
- **WHEN** the user toggles an artist or journey selection
- **THEN** the per-artist counts SHALL remain computed over the full unfiltered loaded set (they SHALL NOT drop as the active filter narrows the highway)

#### Scenario: Pre-selecting current filter
- **WHEN** the bottom sheet opens while a filter is already active
- **THEN** the currently filtered artists SHALL be pre-selected (chips in selected state)

#### Scenario: Chip selected state
- **WHEN** the user taps an artist chip
- **THEN** the chip SHALL display a checkmark and a brand-colour tinted background to indicate selection

#### Scenario: Clear all pending selections
- **WHEN** one or more chips are in the pending-selected state (in any facet)
- **THEN** the "全て解除" button SHALL be enabled
- **WHEN** the user taps "全て解除"
- **THEN** all pending selections across every facet SHALL be cleared (chips return to unselected state)
- **AND** the change SHALL NOT be applied until the user confirms

#### Scenario: Clear all button disabled when nothing selected
- **WHEN** no chips are in the pending-selected state in any facet
- **THEN** the "全て解除" button SHALL be disabled

#### Scenario: Confirming selection
- **WHEN** the user selects artists and taps the confirm button
- **THEN** `filteredArtistIds` SHALL be updated to the selected set
- **THEN** the bottom sheet SHALL close

#### Scenario: Confirming empty selection
- **WHEN** the user deselects all artists (or taps "全て解除") and confirms
- **THEN** the filter SHALL be cleared (equivalent to no filter)

#### Scenario: Sheet snaps flush to viewport bottom
- **WHEN** the filter bottom sheet opens
- **THEN** the sheet body SHALL be snapped flush to the bottom of the viewport via `scroll-snap-align: end` on `.sheet-body`
- **AND** the section content height SHALL be correctly reported to the scroll container (no `fieldset`/`legend` height anomalies)

### Requirement: Push notification deep-link to filtered dashboard
Tapping a push notification that carries a `/dashboard?artists=<artistId>` URL SHALL open the dashboard pre-filtered to that artist.

#### Scenario: Notification tap opens filtered dashboard
- **WHEN** a push notification with `data.url = "/dashboard?artists=<artistId>"` is tapped
- **THEN** the browser SHALL navigate to `/dashboard?artists=<artistId>`
- **THEN** the dashboard SHALL display only concerts for `<artistId>`

#### Scenario: Filter hidden during onboarding
- **WHEN** the user is in the onboarding flow (`isOnboarding` is true)
- **THEN** the filter trigger button SHALL be hidden (via `if.bind="!isOnboarding"`)
- **AND** the `artists` query param SHALL be ignored until onboarding is complete

### Requirement: Filter availability for guest users
The filter trigger and the artist facet SHALL be available to unauthenticated (guest) users, who can follow artists locally. The filter SHALL NOT be gated by authentication; only the onboarding flow suppresses it.

#### Scenario: Guest sees the filter trigger and artist facet
- **WHEN** an unauthenticated (guest) user who has followed at least one artist views the dashboard outside of onboarding
- **THEN** the filter trigger button SHALL be visible
- **AND** opening the sheet SHALL present the artist facet with that guest's followed artists

#### Scenario: Filter still suppressed during onboarding
- **WHEN** the user (guest or authenticated) is in the onboarding flow
- **THEN** the filter trigger SHALL remain hidden

