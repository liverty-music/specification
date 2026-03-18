## ADDED Requirements

### Requirement: Bottom Sheet Custom Element
The system SHALL provide a `<bottom-sheet>` custom element as the single dialog primitive for all overlay content, using the Popover API with CSS scroll-snap dismiss.

#### Scenario: Basic open/close via bindable
- **WHEN** `<bottom-sheet open.bind="isOpen">` has `open` set to `true`
- **THEN** the CE SHALL call `showPopover()` on the internal `<dialog>` element
- **AND** the sheet SHALL animate in from the bottom via CSS `transform: translateY(100%)` → `translateY(0)` using `@starting-style`
- **WHEN** `open` is set to `false`
- **THEN** the CE SHALL call `hidePopover()` and the sheet SHALL animate out

#### Scenario: Scroll-snap dismiss
- **WHEN** the sheet is open and `dismissable` is `true`
- **THEN** a dismiss zone SHALL be rendered above the sheet content as a scroll-snap target
- **AND** swiping down SHALL scroll to the dismiss zone, triggering close on `scrollend`
- **AND** the `::backdrop` opacity SHALL track scroll progress in real-time via a CSS custom property

#### Scenario: Non-dismissable mode
- **WHEN** `dismissable` is `false`
- **THEN** the CE SHALL use `popover="manual"` instead of `popover="auto"`
- **AND** the dismiss zone SHALL NOT be rendered
- **AND** light dismiss (Escape, click-outside) SHALL be disabled

#### Scenario: Dismissable mode with light dismiss
- **WHEN** `dismissable` is `true` (default)
- **THEN** the CE SHALL use `popover="auto"`
- **AND** pressing Escape, clicking outside, or Android back gesture SHALL close the sheet
- **AND** the CE SHALL handle the `toggle` event to detect light dismiss and dispatch `sheet-closed`

#### Scenario: Sheet closed event
- **WHEN** the sheet is closed by any mechanism (light dismiss, scroll-snap, programmatic)
- **THEN** the CE SHALL dispatch a `sheet-closed` CustomEvent with `bubbles: true`
- **AND** the parent component SHALL respond by setting `open` to `false`

#### Scenario: Backdrop click dismiss
- **WHEN** the user clicks the transparent area above the sheet card
- **THEN** the CE SHALL initiate a smooth scroll to the dismiss zone
- **AND** the sheet SHALL close via the scroll-snap dismiss mechanism

#### Scenario: Handle bar rendering
- **WHEN** the sheet is open
- **THEN** a handle bar (2.5rem wide, 0.25rem tall, rounded) SHALL be rendered at the top of the sheet body
- **AND** the handle bar SHALL be styled with `oklch(100% 0 0deg / 20%)` background

#### Scenario: Sheet body structure
- **WHEN** the sheet is rendered
- **THEN** the sheet body SHALL have `border-radius: var(--radius-sheet)` on top corners
- **AND** background SHALL be `var(--color-surface-raised)`
- **AND** box-shadow SHALL be `var(--shadow-sheet)`
- **AND** `max-block-size` SHALL be `90dvh`
- **AND** overflow-y SHALL be `auto` for scrollable content

#### Scenario: Slotted content
- **WHEN** content is placed inside `<bottom-sheet>`
- **THEN** it SHALL be projected via `<au-slot>` into the sheet body below the handle bar

#### Scenario: Focus management
- **WHEN** the sheet opens
- **THEN** the sheet `<dialog>` element SHALL receive focus
- **WHEN** the sheet closes
- **THEN** focus SHALL return to the element that was focused before the sheet opened

#### Scenario: History integration
- **WHEN** the sheet opens
- **THEN** a history entry SHALL NOT be pushed by the CE itself
- **AND** consuming components MAY manage history state independently via `open` binding

#### Scenario: Reduced motion
- **WHEN** `prefers-reduced-motion: reduce` is active
- **THEN** all transition durations SHALL be reduced to `var(--transition-fast)`

#### Scenario: Detach cleanup
- **WHEN** the CE is detached from the DOM while the sheet is open
- **THEN** all event listeners (popstate, toggle) SHALL be removed
- **AND** no memory leaks SHALL occur
