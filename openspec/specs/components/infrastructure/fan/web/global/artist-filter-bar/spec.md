# Artist Filter Bar

## Purpose

Provides the artist selection filter sheet used to narrow the concert list to chosen artists, pre-selecting the user's followed artists and offering a ticket-journey status facet to authenticated users.

## Requirements

### Requirement: Filter sheet initializes selection from followed artists

When the artist filter sheet is opened, it SHALL initialize its selection from the user's currently followed artists, so the displayed selection reflects the user's actual followed artists.

#### Scenario: No followed artists when the sheet opens

- **GIVEN** the user follows no artists
- **WHEN** the filter sheet is opened
- **THEN** the selection SHALL be initialized to empty

#### Scenario: Multiple followed artists when the sheet opens

- **GIVEN** the user follows multiple artists
- **WHEN** the filter sheet is opened
- **THEN** the selection SHALL be initialized with the IDs of all currently followed artists

#### Scenario: Reopening the sheet resets the selection

- **GIVEN** the sheet has been opened and the selection has since been changed
- **WHEN** the sheet is opened again
- **THEN** the selection SHALL be reset to reflect the current followed artists, discarding any prior changes

### Requirement: Journey-status facet in the filter sheet
The filter bottom sheet SHALL present a ticket-journey-status facet as a multi-select chip group, in addition to the artist facet. Statuses SHALL be ordered in journey-flow order with a visual break separating the process phase (`tracking`, `applied`) from the outcome phase (`unpaid`, `paid`, `lost`). Each chip SHALL derive its label, icon, and hue from the canonical journey-status presentation map.

#### Scenario: Facet rendered as its own section
- **WHEN** the filter sheet opens for an authenticated user
- **THEN** the journey-status facet SHALL be rendered as a `<section>` with its own `<h*>` heading, and the chip list SHALL carry `aria-labelledby` referencing that heading

#### Scenario: Status ordering with process/outcome break
- **WHEN** the journey facet is rendered
- **THEN** `tracking` and `applied` SHALL appear first as the process phase
- **AND** a visual break SHALL separate them from the outcome phase `unpaid`, `paid`, `lost` in that order

#### Scenario: Chip selected state
- **WHEN** the user taps a status chip
- **THEN** the chip SHALL fill with that status's semantic hue and indicate selection
- **AND** the unselected chips SHALL remain as neutral outlines that still carry the status icon and label

#### Scenario: Pre-selecting the current journey filter
- **WHEN** the sheet opens while a journey filter is active
- **THEN** the currently filtered statuses SHALL be pre-selected

#### Scenario: Confirming clears or sets the journey filter
- **WHEN** the user changes the status selection and confirms
- **THEN** the active journey filter SHALL be updated to the selected set (empty selection clears the journey filter)

#### Scenario: Clear all covers the journey facet
- **WHEN** the user taps the sheet "全て解除" (Clear all) button
- **THEN** pending journey-status selections SHALL be cleared together with the pending artist selections

### Requirement: Journey facet visible to authenticated users only
The journey-status facet SHALL be rendered only when the user is authenticated. Unauthenticated (guest) users SHALL NOT see the journey facet, and the `journey` query parameter SHALL have no effect for them.

#### Scenario: Authenticated user sees the journey facet
- **WHEN** an authenticated user opens the filter sheet
- **THEN** the journey-status facet SHALL be present in the sheet

#### Scenario: Guest does not see the journey facet
- **WHEN** an unauthenticated (guest) user opens the filter sheet
- **THEN** the journey-status facet SHALL NOT be rendered (absent from the DOM and accessibility tree)
- **AND** the artist facet SHALL still be available

#### Scenario: Sign-in mid-session reveals the facet
- **WHEN** a guest signs in while on the dashboard
- **THEN** the journey-status facet SHALL become available without a full page reload
