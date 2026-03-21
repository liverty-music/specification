## MODIFIED Requirements

### Requirement: Artist List Row

The My Artists list view SHALL render artist hype settings as a semantic HTML table wrapped in a `<fieldset>`. Each artist is a `<tr>` in the `<tbody>`; hype level columns are defined by `<th scope="col">` in the `<thead>`. The `<fieldset>` groups the entire table as a single form control group with a visually hidden `<legend>`.

#### Scenario: Table structure renders correctly

- **WHEN** the My Artists page renders in list view with at least one followed artist
- **THEN** the system SHALL render a `<fieldset>` containing a `<table>`
- **AND** the `<fieldset>` SHALL have a visually hidden `<legend>` that names the group
- **AND** the `<thead>` SHALL contain one `<tr>` with column headers: artist name, 👀 チェック, 🔥 地元, 🔥🔥 近くも, 🔥🔥🔥 どこでも！, and a visually hidden "Remove" column header
- **AND** each `<th scope="col">` in `<thead>` SHALL be sticky at the top of the scroll container with `backdrop-filter: blur(8px)`

#### Scenario: Artist row layout

- **WHEN** an artist row is rendered in list view
- **THEN** the row SHALL be a `<tr>` with a `<th scope="row">` for the artist name and four `<td>` cells for hype level radio inputs
- **AND** the artist name SHALL include a decorative color indicator dot (aria-hidden) and truncate with ellipsis if it exceeds available space
- **AND** a final `<td>` SHALL contain a delete button for that artist
- **AND** the row SHALL carry a `view-transition-name` via CSS custom property for animated removal

#### Scenario: Dot radio input renders per hype cell

- **WHEN** a hype `<td>` renders
- **THEN** the cell SHALL contain a `<label>` wrapping a visually hidden `<input type="radio">` and a visible `<span class="hype-dot">`
- **AND** all four radio inputs in a row SHALL share the same `name` attribute scoped to the artist ID
- **AND** the active dot SHALL be 14px; inactive dots SHALL be 8px
- **AND** each dot SHALL have a minimum 44×44px transparent tap target

#### Scenario: Dot visual reflects hype tier

- **WHEN** the slider renders with a specific hype level selected
- **THEN** the active dot SHALL apply CSS effects based on hype level:
  - watch: `1px solid white/10` border, no glow
  - home: artist-color border at 40% opacity, `box-shadow: 0 0 8px` at 30%
  - nearby: artist-color `2px solid` border, `box-shadow: 0 0 16px` at 50%, gentle pulse animation
  - away: animated border, layered glow (`0 0 24px` at 60% + `0 0 48px` at 20%), strong pulse animation
- **AND** the artist color SHALL be applied via `--_dot-color` CSS custom property on the `<tr>`

#### Scenario: Decorative track line renders between dots

- **WHEN** an artist row renders
- **THEN** a 2px horizontal track line SHALL be visible connecting the four dot positions
- **AND** the track line SHALL be vertically centered in the row
- **AND** the track line SHALL be rendered as a CSS `::before` pseudo-element on each hype `<td>` (`.hype-col`), chaining from the dot center to the next cell

#### Scenario: Reduced motion preference

- **WHEN** the user has `prefers-reduced-motion: reduce` enabled
- **THEN** all pulse animations on active dots SHALL be disabled
- **AND** static border and glow styles SHALL remain visible

#### Scenario: Delete button unfollows artist

- **WHEN** the user taps the delete button in an artist row
- **THEN** the system SHALL optimistically remove the artist from the list
- **AND** if the View Transitions API is available, the remaining rows SHALL animate smoothly to fill the gap
- **AND** the system SHALL display an Undo snack with a 5-second timeout
- **AND** if the user taps Undo within 5 seconds, the artist SHALL be re-inserted at their original position
- **AND** if the Undo snack dismisses without Undo, the system SHALL commit the unfollow via RPC with 1 retry

#### Scenario: Unfollow button is accessible

- **WHEN** an unfollow button renders in an artist row
- **THEN** it SHALL be a `<button type="button">` element
- **AND** it SHALL carry an i18n `aria-label` that includes the artist name (e.g., "Unfollow Suchmos")
- **AND** the trash icon inside SHALL have `aria-hidden="true"`

#### Scenario: Onboarding completes on hype interaction

- **WHEN** the user is on the MY_ARTISTS onboarding step and taps a hype dot
- **THEN** the system SHALL revert the hype change (no mutation)
- **AND** SHALL deactivate the spotlight
- **AND** SHALL advance onboarding to COMPLETED
- **AND** SHALL stay on the My Artists page (no navigation)
- **AND** the signup prompt banner SHALL remain visible for unauthenticated users

## REMOVED Requirements

### Requirement: Artist List Row (swipe-to-dismiss)

**Reason**: The scroll-snap swipe-to-dismiss interaction has zero discoverability, is inaccessible to keyboard and AT users, and is incompatible with `<table><tr>` layout. The Undo toast provides the same safety net. Replaced by an explicit delete button in the row.

**Migration**: Remove `scroll-snap-type: x mandatory` from rows. Remove `checkDismiss`, `executeDismiss`, and `dismissingIds` from `my-artists-route.ts`. Remove `.dismiss-end` element and styles.

### Requirement: Hype slider replaces passion icon

**Reason**: The `hype-inline-slider` custom element is deleted. Dot radio inputs are now rendered directly in `<td>` cells within the table structure. The visual style is preserved.

**Migration**: Remove `<import>` of `hype-inline-slider` from `my-artists-route.html`. Delete `src/components/hype-inline-slider/` directory.
