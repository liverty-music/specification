## MODIFIED Requirements

### Requirement: Bottom Sheet Custom Element
The system SHALL provide a `<bottom-sheet>` custom element as the single dialog primitive for all overlay content, using the Popover API with CSS scroll-snap dismiss.

#### Scenario: Scroll-snap dismiss
- **WHEN** the sheet is open and `dismissable` is `true`
- **THEN** a dismiss zone SHALL be rendered above the sheet content as a direct child of the `dialog` element
- **AND** swiping down SHALL scroll to the dismiss zone, triggering close on `scrollend`
- **AND** the `::backdrop` opacity SHALL track scroll progress via CSS Scroll-Driven Animations (`scroll-timeline` on `dialog`, `animation-timeline` on `dialog::backdrop`)
- **AND** if the browser does not support Scroll-Driven Animations on `::backdrop`, the backdrop SHALL display at static full opacity as a fallback

#### Scenario: DOM structure
- **WHEN** the sheet is rendered
- **THEN** the internal DOM SHALL be `dialog > .dismiss-zone + .sheet-body`
- **AND** the `dialog` element itself SHALL be the scroll-snap container (`overflow-y: auto`, `scroll-snap-type: y mandatory`)
- **AND** no intermediate `.scroll-wrapper` or `.sheet-page` wrapper SHALL exist

#### Scenario: Non-dismissable mode
- **WHEN** `dismissable` is `false`
- **THEN** the CE SHALL use `popover="manual"`
- **AND** the dismiss zone SHALL NOT be rendered
- **AND** scroll-snap dismiss SHALL be disabled
- **AND** ESC key SHALL NOT close the sheet

#### Scenario: Dismissable mode with ESC dismiss
- **WHEN** `dismissable` is `true` (default)
- **THEN** the CE SHALL use `popover="auto"`
- **AND** pressing Escape SHALL close the sheet via the browser's native popover light dismiss
- **AND** the CE SHALL handle the `toggle` event to detect ESC dismiss and dispatch `sheet-closed`
- **AND** backdrop click dismiss SHALL NOT function (the full-viewport dialog has no clickable `::backdrop` area)

## REMOVED Requirements

### Requirement: Bottom Sheet Custom Element

#### Scenario: Backdrop click dismiss
- **WHEN** the user clicks the transparent area above the sheet card
- **THEN** the CE SHALL initiate a smooth scroll to the dismiss zone
- **AND** the sheet SHALL close via the scroll-snap dismiss mechanism

**Reason**: The `.sheet-page` wrapper that created the "transparent area above the sheet card" is removed. The `onBackdropClick` JS handler was the source of the dismiss regression bug. Backdrop click dismiss is also structurally impossible with the full-viewport dialog layout.
**Migration**: No consumer changes required. Scroll-snap dismiss and ESC key dismiss remain as the dismiss mechanisms.
