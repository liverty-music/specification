## MODIFIED Requirements

### Requirement: Filter chip UI in page header

The dashboard filter SHALL be reached from the FAB action launcher (see the
`fab-action-launcher` capability) instead of a dedicated trigger button in the page
header; the page header SHALL NOT host a filter trigger. The launcher's filter item
SHALL visually indicate when a filter is active. Artist names SHALL NOT be rendered
as chips in the header. The filter item SHALL be contributed to the launcher only
while the dashboard is in My Timetable mode.

#### Scenario: No active filter — header unchanged

- **WHEN** `filteredArtistIds` is empty
- **THEN** the launcher's filter item SHALL be in its default (inactive) visual state
- **AND** no artist name chips SHALL be rendered in the header

#### Scenario: Active filter — icon state only

- **WHEN** `filteredArtistIds` contains one or more IDs
- **THEN** the launcher's filter item SHALL display in its active visual state (e.g., color change via `[data-active="true"]` CSS)
- **AND** no artist name chips SHALL be rendered in the header

#### Scenario: Dismissing an active filter

- **WHEN** a filter is active and the user activates the launcher's filter item
- **THEN** the bottom sheet SHALL open with currently filtered artists pre-selected
- **AND** the user can deselect artists and confirm to reduce or clear the filter

#### Scenario: No filter trigger in the header

- **WHEN** the dashboard header is rendered
- **THEN** the header SHALL NOT contain a filter trigger button
- **AND** the filter SHALL be reachable only via the FAB action launcher

### Requirement: Artist-selection bottom sheet

A bottom sheet SHALL allow the user to select one or more followed artists as a
filter. Artists SHALL be presented as pill-shaped chip elements. Each artist chip
SHALL be prefixed with the number of that artist's upcoming concerts in the loaded
dashboard set. The artist chips SHALL be ordered by that concert count descending
(ties broken by artist name ascending), and artists with zero upcoming concerts
SHALL NOT be listed. A "全て解除" (Clear all) button SHALL appear beside the sheet
title and allow the user to deselect all pending selections across every facet in
the sheet before confirming.

The sheet content SHALL be structured as a `<section>` element (not `<fieldset>`)
with an `<h2>` heading as the title. The chip list SHALL carry `aria-labelledby`
referencing the heading ID. `role="group"` SHALL NOT be applied to the `<ul>`
element as it overrides the native `list` role and causes screen readers to lose
item count information.

#### Scenario: Opening the bottom sheet

- **WHEN** the user activates the filter item in the FAB action launcher
- **THEN** the bottom sheet SHALL open listing the followed artists (that have upcoming concerts) as selectable chips
- **AND** the launcher panel SHALL close as the sheet opens

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

### Requirement: Filter availability for guest users

The filter SHALL be available to unauthenticated (guest) users, who can follow
artists locally, via the FAB action launcher's filter item and the artist facet in
the sheet. The filter SHALL NOT be gated by authentication; only the onboarding flow
suppresses it (the filter item is not contributed to the launcher during onboarding).

#### Scenario: Guest sees the filter trigger and artist facet

- **WHEN** an unauthenticated (guest) user who has followed at least one artist views the dashboard outside of onboarding
- **THEN** the FAB action launcher SHALL include the filter item
- **AND** activating it SHALL present the artist facet with that guest's followed artists

#### Scenario: Filter still suppressed during onboarding

- **WHEN** the user (guest or authenticated) is in the onboarding flow
- **THEN** the filter item SHALL NOT be contributed to the launcher
