## ADDED Requirements

### Requirement: URL-driven journey filter
The dashboard SHALL accept a `journey` query parameter containing one or more ticket-journey status values (comma-separated, from `tracking`, `applied`, `unpaid`, `paid`, `lost`). When present, only concerts whose `journeyStatus` is in the listed set SHALL be displayed. When absent or empty, concerts SHALL NOT be constrained by journey status.

#### Scenario: Single status filter from URL
- **WHEN** the user navigates to `/dashboard?journey=unpaid`
- **THEN** only concerts whose `journeyStatus` is `unpaid` SHALL be shown in the concert highway

#### Scenario: Multiple status filter from URL
- **WHEN** the user navigates to `/dashboard?journey=applied,unpaid`
- **THEN** only concerts whose `journeyStatus` is in `{applied, unpaid}` SHALL be shown

#### Scenario: No journey filter — unconstrained by status
- **WHEN** the user navigates to `/dashboard` with no `journey` param
- **THEN** concerts SHALL NOT be filtered by journey status (concerts with no status set SHALL still be shown)

#### Scenario: Concerts without a journey status are excluded when filtering
- **WHEN** a `journey` filter is active
- **AND** the user is authenticated
- **AND** a concert has no `journeyStatus` set
- **THEN** that concert SHALL NOT be shown

#### Scenario: Unknown status value in filter
- **WHEN** a `journey` value contains a token that is not a valid status
- **THEN** that token SHALL be silently ignored; concerts for remaining valid statuses SHALL still be shown

#### Scenario: Filter yields empty result
- **WHEN** the journey filter (combined with any artist filter) has no matching upcoming concerts
- **THEN** the empty-state placeholder SHALL be displayed (same as the no-concerts state)

### Requirement: Journey filter combines with artist filter
When both the artist filter and the journey filter are active, a concert SHALL be shown only if it satisfies BOTH facets. Selections within a single facet SHALL combine as OR; the two facets SHALL combine as AND.

#### Scenario: Both facets active
- **WHEN** the artist filter is `{A, B}` and the journey filter is `{applied, unpaid}`
- **THEN** a concert SHALL be shown only if its `artistId` is in `{A, B}` AND its `journeyStatus` is in `{applied, unpaid}`

#### Scenario: Only journey facet active
- **WHEN** the artist filter is empty and the journey filter is `{paid}`
- **THEN** all followed-artist concerts whose `journeyStatus` is `paid` SHALL be shown regardless of artist

#### Scenario: Only artist facet active
- **WHEN** the journey filter is empty and the artist filter is `{A}`
- **THEN** all of artist A's concerts SHALL be shown regardless of journey status

### Requirement: Journey filter state synchronised with URL
When the user changes the journey filter via the UI, the dashboard URL SHALL be updated to reflect the new state without a full page reload, and the artist and journey parameters SHALL be written together in a single URL update.

#### Scenario: User changes the journey filter
- **WHEN** the user selects journey statuses in the filter sheet and confirms
- **THEN** the browser URL SHALL update to include `journey=<selectedStatuses>` via `history.replaceState`
- **AND** the concert highway SHALL immediately display only matching concerts

#### Scenario: A single URL update writes both facets
- **WHEN** a confirm commits changes to both the artist and journey selections
- **THEN** the URL SHALL be updated exactly once with both `artists` and `journey` parameters reflecting the final state

#### Scenario: Page reload preserves the journey filter
- **WHEN** the user reloads the page while a journey filter is active
- **THEN** the `journey` query param SHALL be re-parsed from the URL and the same filtered view SHALL be restored

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
