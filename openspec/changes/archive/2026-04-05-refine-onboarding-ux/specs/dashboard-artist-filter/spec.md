## MODIFIED Requirements

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

## REMOVED Requirements

### Requirement: Active filter — chips displayed (REMOVED)
**Reason**: Chips consume significant header space and duplicate artist names already visible in the concert highway. The filter icon's active state (color change) is sufficient affordance for a secondary feature. Simplifying the header improves visual hierarchy.
**Migration**: Remove the `<ul class="chips-list">` block and associated CSS from `artist-filter-bar.html` and `artist-filter-bar.css`. The `dismiss(id)` method in `artist-filter-bar.ts` may be removed if it is only used by the chip dismiss button.

### Requirement: Long artist name overflow (REMOVED)
**Reason**: Chips are removed; overflow truncation is no longer needed.
**Migration**: Remove chip overflow CSS rules from `artist-filter-bar.css`.
