## MODIFIED Requirements

### Requirement: Artist-selection bottom sheet
A bottom sheet SHALL allow the user to select one or more followed artists as a filter. Artists SHALL be presented as pill-shaped chip elements. A "全て解除" (Clear all) button SHALL appear beside the sheet title and allow the user to deselect all pending selections before confirming.

The sheet content SHALL be structured as a `<section>` element (not `<fieldset>`) with an `<h2>` heading as the title. The chip list SHALL carry `aria-labelledby` referencing the heading ID. `role="group"` SHALL NOT be applied to the `<ul>` element as it overrides the native `list` role and causes screen readers to lose item count information.

#### Scenario: Opening the bottom sheet
- **WHEN** the user taps the filter trigger button
- **THEN** the bottom sheet SHALL open listing all followed artists as selectable chips

#### Scenario: Pre-selecting current filter
- **WHEN** the bottom sheet opens while a filter is already active
- **THEN** the currently filtered artists SHALL be pre-selected (chips in selected state)

#### Scenario: Chip selected state
- **WHEN** the user taps an artist chip
- **THEN** the chip SHALL display a checkmark and a brand-colour tinted background to indicate selection

#### Scenario: Clear all pending selections
- **WHEN** one or more chips are in the pending-selected state
- **THEN** the "全て解除" button SHALL be enabled
- **WHEN** the user taps "全て解除"
- **THEN** all pending selections SHALL be cleared (chips return to unselected state)
- **AND** the change SHALL NOT be applied until the user confirms

#### Scenario: Clear all button disabled when nothing selected
- **WHEN** no chips are in the pending-selected state
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

#### Scenario: Filter hidden during onboarding
- **WHEN** the user is in the onboarding flow (`isOnboarding` is true)
- **THEN** the filter trigger button SHALL be hidden (via `if.bind="!isOnboarding"`)
- **AND** the `artists` query param SHALL be ignored until onboarding is complete
