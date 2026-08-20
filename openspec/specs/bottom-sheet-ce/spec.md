# Bottom Sheet Custom Element

## Purpose

Provides a `<bottom-sheet>` custom element as the single dialog primitive for all overlay content, using a native `<dialog>` element opened via `showModal()` with CSS scroll-snap dismiss via an internal scroll container.

## Requirements
### Requirement: Bottom Sheet Custom Element
The system SHALL provide a `<bottom-sheet>` custom element as the single dialog primitive for all overlay content, using a native `<dialog>` element opened via `showModal()` (promoted to the Top Layer with native focus-trap, `inert` background, and close-request handling) with CSS scroll-snap dismiss via an internal scroll container. User-initiated swipe-to-dismiss SHALL be detected via the `scrollsnapchange` event, which by specification fires only for a user scroll gesture and not for programmatic or initial-layout snap changes. The CE host (`<bottom-sheet>`) SHALL wrap an inner `<dialog>` element; the scroll container, dismiss zone, and sheet body SHALL live inside that `<dialog>`.

#### Scenario: Basic open/close via bindable
- **WHEN** `<bottom-sheet open.bind="isOpen">` has `open` set to `true`
- **THEN** the CE SHALL call `showModal()` on the inner `<dialog>` element (via `ref`)
- **AND** the `<dialog>` SHALL be promoted to the Top Layer with the rest of the document made `inert`
- **AND** the sheet-body SHALL be visible at the bottom of the viewport via CSS `initial-snap` animation (no JS `scrollTo` required)
- **WHEN** `open` is set to `false`
- **THEN** the CE SHALL call `close()` on the inner `<dialog>` and the sheet SHALL animate out within 160ms

#### Scenario: Open bound to true at component creation time
- **WHEN** `open` is bound to `true` at initial bind time (before `attached()`)
- **AND** `openChanged(true)` is called during the `binding` phase
- **THEN** `showModal()` SHALL be called but MAY fail silently if the inner `<dialog>` ref is not yet resolved
- **AND** the error SHALL be caught and suppressed (matching the existing `close()` try-catch pattern)
- **AND** the `attached()` lifecycle hook SHALL retry via `if (this.open) this.openChanged(true)` after the `<dialog>` ref is initialized
- **AND** the sheet SHALL open successfully at `attached()` time

#### Scenario: DOM structure
- **WHEN** the sheet is rendered
- **THEN** the CE host (`<bottom-sheet>`) SHALL contain an inner `<dialog>` element as the Top-Layer / modal host
- **AND** the `<dialog>` SHALL have an accessible name (`aria-label` or `aria-labelledby`) and SHALL NOT require a manually-set `role` (the native `<dialog>` role suffices)
- **AND** the internal DOM SHALL be `dialog > .scroll-area > .dismiss-zone + section.sheet-body`
- **AND** `.scroll-area` SHALL be a `<div>` element serving as the scroll-snap container (`overflow-y: auto`, `scroll-snap-type: y mandatory`, `block-size: 100dvh`)
- **NOTE** `.scroll-area` MUST use `100dvh` (not `100%`) because percentage block-size does not resolve against the `<dialog>`'s fixed-position height inside the Top Layer — the scroll container would expand to content size, preventing overflow and disabling scroll-snap
- **AND** `.sheet-body` SHALL be a `<section>` element (semantic content container) with `contain: layout`
- **AND** the `::backdrop` pseudo-element SHALL belong to the inner `<dialog>`

#### Scenario: Background inert and focus trap
- **WHEN** the sheet is open (`showModal()`)
- **THEN** all content outside the `<dialog>` SHALL be `inert` (not focusable, not reachable by Tab or assistive technology)
- **AND** keyboard focus SHALL be trapped within the `<dialog>` until it closes

#### Scenario: Layout stability with dynamic sheet content
- **WHEN** content inside `.sheet-body` changes layout (e.g., a checkbox is checked, an element toggles `display`)
- **THEN** `.sheet-body` SHALL remain at the bottom of the viewport
- **AND** `.scroll-area` SHALL NOT be displaced from its rendered position
- **NOTE** This is enforced by `contain: layout` on `.sheet-body`. Without it, Chromium's scroll-snap re-evaluation inside a Top-Layer container incorrectly offsets `.scroll-area` by `-scrollTop` pixels when a child layout change triggers a re-snap. This is a Chromium rendering bug. `contain: layout` prevents child layout changes from propagating to `.scroll-area`. When Chromium fixes this bug, `contain: layout` MAY be removed — the regression guard is the artist-filter chip-check E2E test.

#### Scenario: Initial snap animation
- **WHEN** the `<dialog>` opens (`showModal()`)
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
- **AND** swiping down (physical gesture: finger moves downward, scrollTop decreases) SHALL scroll toward the dismiss zone at the top

#### Scenario: Responsive swipe-down dismiss detection
- **WHEN** the user swipes down (finger moves downward), and the user's scroll gesture rests on the dismiss zone as the new snap target
- **THEN** the CE SHALL detect the dismiss via the `scrollsnapchange` event (whose `snapTargetBlock` is the dismiss zone)
- **AND** the CE SHALL set `open` to `false`, call `close()`, and dispatch `sheet-closed`
- **AND** the close SHALL NOT be gated on any `scrollend` settle, so dismiss does not wait on UA-controlled settle latency
- **NOTE** `scrollsnapchange` fires only for a user scroll gesture (per the CSS Scroll Snap module), so a programmatic or initial-layout re-snap to the dismiss zone SHALL NOT trigger dismiss. This replaces the prior scroll-ratio threshold detection.

#### Scenario: Early close on pointerup at dismiss threshold
- **WHEN** the user lifts their pointer (`pointerup`) while the scroll position is near the dismiss zone but no user-gesture snap change to the dismiss zone has occurred
- **THEN** the CE SHALL NOT close the sheet based on a `scrollTop / maxScroll` ratio threshold
- **AND** the prior `pointerup` (`scrollTop/max < 0.25`) and `scrollend` (`scrollRatio < 0.1`) early-close heuristics SHALL be removed, because they fire on the programmatic initial re-snap and caused the iOS/WebKit "flash then close" defect
- **NOTE** Dismiss is now driven by `scrollsnapchange` (user-gesture-only) with an `IntersectionObserver` fallback; there is no scroll-ratio early-close path. (Title retained for spec-delta continuity; behavior is the removal of the heuristic.)

#### Scenario: Dismiss detection ignores programmatic and initial-snap scroll
- **WHEN** the sheet opens and the `initial-snap` sequence (or any programmatic scroll) momentarily rests the scroll position on the dismiss zone before settling on `.sheet-body`
- **THEN** the CE SHALL NOT dismiss the sheet
- **AND** dismiss SHALL be honored only for a user-initiated scroll gesture (as signalled by `scrollsnapchange` or, on non-supporting engines, by the fallback described below combined with a just-opened guard)
- **NOTE** This prevents the iOS/WebKit "flash then close" defect, where the programmatic re-snap trace (scroll ratio `1 → 0`) was previously misread as a user swipe-to-dismiss by scroll-ratio heuristics.

#### Scenario: Fallback dismiss detection where scrollsnapchange is unsupported
- **WHEN** the engine does not support `scrollsnapchange` (e.g., Firefox)
- **THEN** the CE SHALL detect a user swipe-to-dismiss via an `IntersectionObserver` that observes the dismiss zone / sheet-body crossing the viewport, rather than via `scrollend`/`pointerup` scroll-ratio heuristics
- **AND** the fallback SHALL be armed only after the sheet has opened and settled on `.sheet-body`, so the initial snap does not trigger dismiss

#### Scenario: Just-opened dismiss guard
- **WHEN** the sheet has just been opened (during the open transition / before it has settled on `.sheet-body`)
- **THEN** the CE SHALL suppress any dismiss signal, so the sheet cannot close itself before the user interacts
- **AND** the guard SHALL release once the sheet has settled on `.sheet-body`

#### Scenario: Bounce-back prevention after dismiss-zone snap
- **WHEN** a user scroll gesture changes the scroll-snap target to the dismiss zone (detected via `scrollsnapchange`)
- **THEN** the CE SHALL immediately set `pointer-events: none` on `.scroll-area`
- **AND** any subsequent upward swipe input SHALL be ignored by the scroll container
- **AND** the sheet SHALL NOT re-snap to `.sheet-body` after the dismiss-zone snap is detected
- **AND** `pointer-events` SHALL be restored to its default value in `onClose()`

#### Scenario: Close animation completes within 160ms
- **WHEN** the sheet is dismissed by any mechanism (swipe, tap-outside, ESC)
- **THEN** the close transition (opacity + overlay + display) SHALL complete within 160ms
- **NOTE** This replaces the prior 240ms duration; the shorter duration reduces perceived latency after the swipe gesture

#### Scenario: Tap-outside dismiss
- **WHEN** the sheet is open and `dismissable` is `true`
- **AND** the user taps/clicks the dimmed area above the sheet body (the `.dismiss-zone`)
- **THEN** the CE SHALL set `open` to `false`, call `close()`, and dispatch `sheet-closed`
- **NOTE** Tap-outside is implemented as a `click` handler on the `.dismiss-zone` element, NOT via `::backdrop` and NOT via `closedby`: under full-viewport coverage the dialog box occludes the backdrop, so every tap targets a `<dialog>` descendant and neither the `::backdrop` (the `event.target === dialog` light-dismiss pattern) nor `closedby` native light-dismiss ever fires. (The `[popover]::backdrop { pointer-events: none }` UA rule applies to popovers, not `<dialog>::backdrop`, so it is not the reason here.)
- **WHEN** `dismissable` is `false`
- **THEN** the `.dismiss-zone` tap SHALL NOT close the sheet

#### Scenario: Gesture-coupled backdrop fade
- **WHEN** the browser supports scroll-driven animations (`@supports (animation-timeline: scroll())`)
- **THEN** the `::backdrop` opacity (and its blur) SHALL be driven by the `.scroll-area` scroll position via `animation-timeline: scroll()`, so the backdrop fades as the user swipes the sheet toward the dismiss zone and is fully cleared by the dismiss threshold
- **WHEN** the browser does NOT support scroll-driven animations (e.g., Firefox)
- **THEN** the `::backdrop` SHALL fall back to an opacity `transition` on open/close (the prior behavior)

#### Scenario: Non-dismissable mode
- **WHEN** `dismissable` is `false`
- **THEN** the inner `<dialog>` SHALL be opened with `showModal()` and SHALL suppress close requests (the `cancel` event SHALL be `preventDefault()`-ed so ESC / Android back do NOT close it)
- **AND** `.scroll-area` SHALL have `data-dismissable="false"`
- **AND** the dismiss zone SHALL remain in the DOM with `aria-hidden="true"` (required for the `initial-snap` animation pattern)
- **AND** CSS SHALL set `.dismiss-zone` to `scroll-snap-align: none` and `pointer-events: none` via `.scroll-area:not([data-dismissable="true"]) .dismiss-zone`
- **AND** `.sheet-body` SHALL be the only active snap target, ensuring the sheet body is visible on open

#### Scenario: Dismissable mode with close-request dismiss (ESC / Android back)
- **WHEN** `dismissable` is `true` (default)
- **THEN** pressing Escape (desktop) or the Android back gesture/button SHALL close the sheet via the `<dialog>`'s native close request
- **AND** the CE SHALL handle the `cancel` (and/or `close`) event on the inner `<dialog>` to set `open` to `false` and dispatch `sheet-closed`

#### Scenario: Sheet closed event
- **WHEN** the sheet is closed by any mechanism (ESC / Android back, tap-outside, scroll-snap swipe, programmatic)
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
- **THEN** `showModal()` SHALL move focus into the `<dialog>` and trap it there
- **WHEN** the sheet closes
- **THEN** focus SHALL return to the element that was focused before the sheet opened

#### Scenario: History integration
- **WHEN** the sheet opens
- **THEN** a history entry SHALL NOT be pushed by the CE itself
- **AND** consuming components MAY manage history state independently via `open` binding

#### Scenario: Reduced motion
- **WHEN** `prefers-reduced-motion: reduce` is active
- **THEN** all transition durations SHALL be reduced to `var(--_duration-reduced)`
- **AND** the scroll-driven backdrop fade SHALL likewise resolve to an instant open/close

#### Scenario: Detach cleanup
- **WHEN** the CE is detached from the DOM while the sheet is open
- **THEN** all event listeners (`cancel`/`close`, `.dismiss-zone` click, `scrollsnapchange`, and any `IntersectionObserver`) SHALL be removed / disconnected
- **AND** `close()` SHALL be called on the inner `<dialog>`
- **AND** `pointer-events` on `.scroll-area` SHALL be restored to its default value
- **AND** no memory leaks SHALL occur

