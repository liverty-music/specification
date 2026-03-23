## CHANGED Requirements

### Requirement: DOM Structure (CHANGED)

The bottom sheet DOM SHALL separate popover responsibility from scroll responsibility.

#### Scenario: DOM structure
- **WHEN** the sheet is rendered
- **THEN** the CE host element (`<bottom-sheet>`) SHALL be the popover host via `host.setAttribute('popover', ...)`
- **AND** the CE host SHALL have `role="dialog"` and `aria-label` set programmatically
- **AND** the internal DOM SHALL be `.scroll-area > .dismiss-zone + section.sheet-body`
- **AND** `.scroll-area` SHALL be the scroll-snap container (`overflow-y: auto`, `scroll-snap-type: y mandatory`)
- **AND** `.sheet-body` SHALL be a `<section>` element (semantic content container)

### Requirement: Non-Dismissable Mode (CHANGED)

When `dismissable` is `false`, the dismiss zone SHALL remain in the DOM but its scroll-snap behavior SHALL be disabled via CSS.

#### Scenario: Non-dismissable sheet opens to sheet body
- **WHEN** `dismissable` is `false`
- **THEN** the CE SHALL use `popover="manual"`
- **AND** `.dismiss-zone` SHALL remain in the DOM with `aria-hidden="true"`
- **AND** `.scroll-area` SHALL have `data-dismissable="false"`
- **AND** CSS SHALL set `.dismiss-zone` to `scroll-snap-align: none` and `pointer-events: none` via `.scroll-area:not([data-dismissable="true"]) .dismiss-zone`
- **AND** the browser SHALL snap to `.sheet-body` (the only active snap target) on open
- **AND** ESC key SHALL NOT close the sheet

#### Scenario: Dismissable sheet enables dismiss zone snap
- **WHEN** `dismissable` is `true` (default)
- **THEN** `.scroll-area` SHALL have `data-dismissable="true"`
- **AND** `.dismiss-zone` SHALL have `scroll-snap-align: var(--_snap-align, start)`
- **AND** swiping down SHALL scroll toward the dismiss zone, triggering close on `scrollend`

### Requirement: Initial Snap Animation (NEW)

The scroll-area SHALL use a CSS `initial-snap` animation to ensure the sheet body is the initial snap target on open, regardless of dismiss-zone presence.

#### Scenario: Sheet opens snapped to body
- **WHEN** `showPopover()` is called on the CE host
- **THEN** `.scroll-area` SHALL run an `initial-snap` animation (`0.01s`, `backwards` fill)
- **AND** during the animation, `--_snap-align` SHALL be `none`, disabling dismiss-zone snap
- **AND** after the animation completes, dismiss-zone snap SHALL restore to its CSS-determined value
- **AND** no JavaScript `scrollTo()` or `requestAnimationFrame` SHALL be required

### Requirement: Basic Open/Close (CHANGED)

#### Scenario: Open via bindable
- **WHEN** `open` is set to `true`
- **THEN** the CE SHALL call `showPopover()` on the CE host element (not an internal dialog)
- **AND** the sheet body SHALL be visible at the bottom of the viewport via CSS scroll-snap (no JS scroll required)

#### Scenario: Close via bindable
- **WHEN** `open` is set to `false`
- **THEN** the CE SHALL call `hidePopover()` on the CE host element
- **AND** the sheet SHALL animate out via CSS opacity transition

### Requirement: Semantic Host Element (NEW)

The CE host SHALL have `role="dialog"` set programmatically in `attached()`, providing dialog semantics without requiring an internal `<dialog>` element.

#### Scenario: Host has dialog role
- **WHEN** the CE is attached to the DOM
- **THEN** `host.setAttribute('role', 'dialog')` SHALL be called
- **AND** `host.setAttribute('aria-label', ...)` SHALL be called with the `ariaLabel` bindable value
