# Bottom Sheet Custom Element

## Purpose

Provides a `<bottom-sheet>` custom element as the single dialog primitive for all overlay content, using the Popover API on the CE host element with CSS scroll-snap dismiss via an internal scroll container.

## Requirements

### Requirement: Bottom Sheet Custom Element
The system SHALL provide a `<bottom-sheet>` custom element as the single dialog primitive for all overlay content, using the Popover API on the CE host element with CSS scroll-snap dismiss via an internal scroll container.

#### Scenario: Basic open/close via bindable
- **WHEN** `<bottom-sheet open.bind="isOpen">` has `open` set to `true`
- **THEN** the CE SHALL call `showPopover()` on the CE host element (via `resolve(INode)`)
- **AND** the sheet-body SHALL be visible at the bottom of the viewport via CSS `initial-snap` animation (no JS `scrollTo` required)
- **WHEN** `open` is set to `false`
- **THEN** the CE SHALL call `hidePopover()` on the CE host element and the sheet SHALL animate out

#### Scenario: Open bound to true at component creation time
- **WHEN** `open` is bound to `true` at initial bind time (before `attached()`)
- **AND** `openChanged(true)` is called during the `binding` phase
- **THEN** `showPopover()` SHALL be called but MAY fail silently if the `popover` attribute is not yet set
- **AND** the error SHALL be caught and suppressed (matching the existing `hidePopover()` try-catch pattern)
- **AND** the `attached()` lifecycle hook SHALL retry via `if (this.open) this.openChanged(true)` after the `popover` attribute is initialized
- **AND** the sheet SHALL open successfully at `attached()` time

#### Scenario: DOM structure
- **WHEN** the sheet is rendered
- **THEN** the CE host element (`<bottom-sheet>`) SHALL be the popover host with `popover` attribute set programmatically
- **AND** the CE host SHALL have `role="dialog"` set in `attached()`
- **AND** the internal DOM SHALL be `.scroll-area > .dismiss-zone + section.sheet-body`
- **AND** `.scroll-area` SHALL be a `<div>` element serving as the scroll-snap container (`overflow-y: auto`, `scroll-snap-type: y mandatory`, `block-size: 100dvh`)
- **NOTE** `.scroll-area` MUST use `100dvh` (not `100%`) because percentage block-size does not resolve against the CE host's fixed-position height inside the popover top-layer — the scroll container would expand to content size, preventing overflow and disabling scroll-snap
- **AND** `.sheet-body` SHALL be a `<section>` element (semantic content container) with `contain: layout`
- **AND** the `::backdrop` pseudo-element SHALL belong to the CE host (popover host)

#### Scenario: Layout stability with dynamic sheet content
- **WHEN** content inside `.sheet-body` changes layout (e.g., a checkbox is checked, an element toggles `display`)
- **THEN** `.sheet-body` SHALL remain at the bottom of the viewport
- **AND** `.scroll-area` SHALL NOT be displaced from its rendered position
- **NOTE** This is enforced by `contain: layout` on `.sheet-body`. Without it, Chromium's scroll-snap re-evaluation inside a popover top-layer incorrectly offsets `.scroll-area` by `-scrollTop` pixels when a child layout change triggers a re-snap. This is a Chromium rendering bug (scroll container offset on snap re-evaluation inside top-layer). `contain: layout` prevents child layout changes from propagating to `.scroll-area`, avoiding the re-evaluation. When Chromium fixes this bug, `contain: layout` MAY be removed — the regression guard is the artist-filter chip-check E2E test.

#### Scenario: Initial snap animation
- **WHEN** the popover opens (`showPopover()` on CE host)
- **THEN** `.scroll-area` SHALL run an `initial-snap` CSS animation (`0.01s`, `animation-fill-mode: backwards`)
- **AND** during the animation, `--_snap-align` SHALL be `none`, disabling dismiss-zone's scroll-snap-align
- **AND** `.sheet-body` (`scroll-snap-align: end`) SHALL be the only active snap target
- **AND** the browser SHALL snap to `.sheet-body` on open
- **AND** after the animation completes, dismiss-zone snap SHALL restore to its CSS-determined value
- **AND** no JavaScript `scrollTo()` or `requestAnimationFrame` SHALL be required

#### Scenario: Scroll-snap dismiss
- **WHEN** the sheet is open and `dismissable` is `true`
- **THEN** `.scroll-area` SHALL have `data-dismissable="true"`
- **AND** the dismiss zone SHALL have `scroll-snap-align: var(--_snap-align, start)` (active after initial-snap animation)
- **AND** swiping down (physical gesture: finger moves downward, scrollTop decreases) SHALL scroll toward the dismiss zone at the top, triggering close on `scrollend`

#### Scenario: Swipe-down dismiss detection
- **WHEN** the user swipes down (finger moves downward), decreasing scrollTop toward the dismiss zone
- **AND** the `scrollend` event fires on `.scroll-area`
- **THEN** the CE SHALL check if `scrollRatio < 0.1` (scrolled near the top where the dismiss zone is)
- **AND** if so, the CE SHALL set `open` to `false` and dispatch `sheet-closed`

#### Scenario: Non-dismissable mode
- **WHEN** `dismissable` is `false`
- **THEN** the CE SHALL use `popover="manual"` on the CE host
- **AND** `.scroll-area` SHALL have `data-dismissable="false"`
- **AND** the dismiss zone SHALL remain in the DOM with `aria-hidden="true"` (required for `initial-snap` animation pattern)
- **AND** CSS SHALL set `.dismiss-zone` to `scroll-snap-align: none` and `pointer-events: none` via `.scroll-area:not([data-dismissable="true"]) .dismiss-zone`
- **AND** `.sheet-body` SHALL be the only active snap target, ensuring the sheet body is visible on open
- **AND** ESC key SHALL NOT close the sheet

#### Scenario: Dismissable mode with ESC dismiss
- **WHEN** `dismissable` is `true` (default)
- **THEN** the CE SHALL use `popover="auto"` on the CE host
- **AND** pressing Escape SHALL close the sheet via the browser's native popover light dismiss
- **AND** the CE SHALL handle the `toggle` event on the CE host to detect ESC dismiss and dispatch `sheet-closed`

#### Scenario: Sheet closed event
- **WHEN** the sheet is closed by any mechanism (ESC dismiss, scroll-snap, programmatic)
- **THEN** the CE SHALL dispatch a `sheet-closed` CustomEvent with `bubbles: true`
- **AND** the parent component SHALL respond by setting `open` to `false`

#### Scenario: Handle bar rendering
- **WHEN** the sheet is open
- **THEN** a handle bar (2.5rem wide, 0.25rem tall, rounded) SHALL be rendered at the top of the sheet body
- **AND** the handle bar SHALL be styled with `oklch(100% 0 0deg / 20%)` background

#### Scenario: Sheet body structure
- **WHEN** the sheet is rendered
- **THEN** the sheet body (`<section>`) SHALL have `border-radius: var(--radius-sheet)` on top corners
- **AND** background SHALL be `var(--color-surface-raised)`
- **AND** box-shadow SHALL be `var(--shadow-sheet)`
- **AND** `max-block-size` SHALL be `90dvh`
- **AND** overflow-y SHALL be `auto` for scrollable content
- **AND** `contain` SHALL be `layout` (layout containment boundary — see layout stability scenario)

#### Scenario: Slotted content
- **WHEN** content is placed inside `<bottom-sheet>`
- **THEN** it SHALL be projected via `<au-slot>` into the sheet body below the handle bar

#### Scenario: Focus management
- **WHEN** the sheet opens
- **THEN** the CE host element SHALL receive focus via `showPopover()`
- **WHEN** the sheet closes
- **THEN** focus SHALL return to the element that was focused before the sheet opened

#### Scenario: History integration
- **WHEN** the sheet opens
- **THEN** a history entry SHALL NOT be pushed by the CE itself
- **AND** consuming components MAY manage history state independently via `open` binding

#### Scenario: Reduced motion
- **WHEN** `prefers-reduced-motion: reduce` is active
- **THEN** all transition durations SHALL be reduced to `var(--_duration-reduced)`

#### Scenario: Detach cleanup
- **WHEN** the CE is detached from the DOM while the sheet is open
- **THEN** all event listeners (toggle) SHALL be removed from the CE host
- **AND** `hidePopover()` SHALL be called on the CE host
- **AND** no memory leaks SHALL occur
