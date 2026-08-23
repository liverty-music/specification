# Bottom Sheet Custom Element

## Purpose

Provides a `<bottom-sheet>` custom element as the single dialog primitive for all overlay content, promoted to the Top Layer via a non-modal `popover` (`<dialog popover="manual">` shown with `showPopover()`), with CSS scroll-snap dismiss driven by an `IntersectionObserver` on the sheet body; focus-trap, background `inert`, and Escape are managed by the component.

## Requirements
### Requirement: Bottom Sheet Custom Element
The system SHALL provide a `<bottom-sheet>` custom element as the single dialog primitive for all overlay content, promoted to the Top Layer via a **non-modal `popover="manual"`** element (NOT `<dialog>.showModal()`), with CSS scroll-snap dismiss via an internal scroll container. The open/closed lifecycle SHALL be driven by an `IntersectionObserver` on the sheet body as the single source of truth: all dismiss paths (swipe, tap-outside, ESC, Android back, programmatic) converge in its callback. Dismissing SHALL be performed by scrolling the container to the closed snap stop; the popover SHALL be hidden (`hidePopover()`) only after the observer confirms the sheet has left the viewport, so the dismiss scroll itself is the (native, momentum-driven, interruptible) close animation. Because a `popover` is non-modal, the CE SHALL manage focus-trap, background `inert`, and the Escape close request itself.

#### Scenario: Basic open/close via bindable
- **WHEN** `<bottom-sheet open.bind="isOpen">` has `open` set to `true`
- **THEN** the CE SHALL call `showPopover()` on the popover element (via `ref`)
- **AND** the popover SHALL be promoted to the Top Layer
- **AND** the CE SHALL set the rest of the document `inert` and move focus into the sheet body
- **AND** the sheet-body SHALL be visible at the bottom of the viewport via the CSS `initial-snap` animation (no JS `scrollTo` required on open)
- **WHEN** `open` is set to `false`
- **THEN** the CE SHALL scroll `.scroll-area` to the closed snap stop (the dismiss zone) and SHALL call `hidePopover()` only after the `IntersectionObserver` reports the sheet body has left the viewport

#### Scenario: Open bound to true at component creation time
- **WHEN** `open` is bound to `true` at initial bind time (before `attached()`)
- **AND** `openChanged(true)` is called during the `binding` phase
- **THEN** `showPopover()` SHALL be called but MAY fail silently if the popover ref is not yet resolved
- **AND** the error SHALL be caught and suppressed (matching the existing `hidePopover()` try-catch pattern)
- **AND** the `attached()` lifecycle hook SHALL retry via `if (this.open) this.openChanged(true)` after the popover ref is initialized
- **AND** the sheet SHALL open successfully at `attached()` time

#### Scenario: DOM structure
- **WHEN** the sheet is rendered
- **THEN** the CE host (`<bottom-sheet>`) SHALL contain a popover element (`popover="manual"`) as the Top-Layer host
- **AND** the popover host SHALL have an accessible name (`aria-label` or `aria-labelledby`) and SHALL carry `role="dialog"` and `aria-modal="true"` (a `popover` has no implicit dialog semantics, so these SHALL be set explicitly)
- **AND** the internal DOM SHALL be `[popover] > .scroll-area > .dismiss-zone + section.sheet-body`
- **AND** `.scroll-area` SHALL be a `<div>` element serving as the scroll-snap container (`overflow-y: auto`, `scroll-snap-type: y mandatory`, `block-size: 100svh`, `overscroll-behavior: none`)
- **NOTE** `.scroll-area` MUST use viewport-relative height (`100svh`, not `100%`) because percentage block-size does not resolve against the popover's fixed-position height inside the Top Layer — the scroll container would expand to content size, preventing overflow and disabling scroll-snap. `svh` (not `dvh`/`vh`) is used so the height does not jump when the iOS Safari address bar resizes mid-swipe.
- **AND** `.sheet-body` SHALL be a `<section>` element (semantic content container) with `contain: layout`
- **AND** the `::backdrop` pseudo-element SHALL belong to the popover host

#### Scenario: Background inert and focus trap
- **WHEN** the sheet is open
- **THEN** the CE SHALL make all content outside the popover `inert` (not focusable, not reachable by Tab or assistive technology)
- **AND** keyboard focus SHALL be trapped within the sheet until it closes
- **NOTE** Because `popover` (unlike `<dialog>.showModal()`) does not provide `inert` or a focus trap natively, the CE SHALL apply `inert` to the document (or the app shell root) while open and remove it on close.

#### Scenario: Background interactive during the close animation
- **WHEN** the user dismisses the sheet and the close scroll begins
- **THEN** the CE SHALL lift the background `inert` as soon as the dismiss is underway (not only after the popover is fully hidden)
- **AND** the user SHALL be able to interact with background content (e.g. tap another concert card) during the close animation without waiting for the sheet to fully close
- **NOTE** This removes the prior "operation lock", where the modal `<dialog>` `::backdrop` plus `overlay ... allow-discrete` blocked all background pointer events for the entire close animation.

#### Scenario: Layout stability with dynamic sheet content
- **WHEN** content inside `.sheet-body` changes layout (e.g., a checkbox is checked, an element toggles `display`)
- **THEN** `.sheet-body` SHALL remain at the bottom of the viewport
- **AND** `.scroll-area` SHALL NOT be displaced from its rendered position
- **NOTE** This is enforced by `contain: layout` on `.sheet-body`. Without it, Chromium's scroll-snap re-evaluation inside a Top-Layer container incorrectly offsets `.scroll-area` by `-scrollTop` pixels when a child layout change triggers a re-snap. This is a Chromium rendering bug. `contain: layout` prevents child layout changes from propagating to `.scroll-area`. When Chromium fixes this bug, `contain: layout` MAY be removed — the regression guard is the artist-filter chip-check E2E test.

#### Scenario: Initial snap animation
- **WHEN** the popover opens (`showPopover()`)
- **THEN** `.scroll-area` SHALL run an `initial-snap` CSS animation (`0.01s`, `animation-fill-mode: backwards`)
- **AND** during the animation, `--_snap-align` SHALL be `none`, disabling dismiss-zone's scroll-snap-align
- **AND** `.sheet-body` (`scroll-snap-align: end`) SHALL be the only active snap target
- **AND** the browser SHALL snap to `.sheet-body` on open
- **AND** after the animation completes, dismiss-zone snap SHALL restore to its CSS-determined value
- **AND** no JavaScript `scrollTo()` or `requestAnimationFrame` SHALL be required on open in browsers that support the keyframe hack
- **NOTE** The cross-browser `initial-snap` keyframe hack is retained deliberately. The declarative `scroll-initial-target: nearest` alternative is Chromium-only (unsupported in Safari and Firefox as of 2026-08) and not Baseline; it SHALL replace the keyframe hack only after it reaches Baseline.

#### Scenario: Scroll-snap dismiss
- **WHEN** the sheet is open and `dismissable` is `true`
- **THEN** `.scroll-area` SHALL have `data-dismissable="true"`
- **AND** the dismiss zone SHALL have `scroll-snap-align: var(--_snap-align, start)` (active after the initial-snap animation)
- **AND** swiping down (physical gesture: finger moves downward, scrollTop decreases) SHALL scroll toward the dismiss zone at the top
- **AND** `overscroll-behavior: none` SHALL prevent the dismiss swipe from chaining into page scroll

#### Scenario: Responsive swipe-down dismiss detection
- **WHEN** the user swipes the sheet down so the sheet body scrolls off the viewport (the dismiss zone becomes the settled snap target)
- **THEN** the CE SHALL detect the dismiss via an `IntersectionObserver` observing the sheet body's visibility within the popover
- **AND** on the sheet body leaving the viewport the CE SHALL call `hidePopover()`, set `open` to `false`, and dispatch `sheet-closed`
- **AND** dismiss detection SHALL NOT depend on any `scrollTop / maxScroll` ratio threshold, nor on committing `close()` on the `scrollsnapchange` event
- **NOTE** The `IntersectionObserver` fires regardless of how the sheet moved (user swipe, programmatic close scroll, or snap settle), so every dismiss path converges in one callback. This replaces the prior `scrollsnapchange` + scroll-ratio detection.

#### Scenario: Early close on pointerup at dismiss threshold
- **WHEN** the user lifts their pointer (`pointerup`) at any scroll position
- **THEN** the CE SHALL NOT close the sheet based on a `scrollTop / maxScroll` ratio threshold
- **AND** the prior `pointerup` (`scrollTop/max < 0.25`) and `scrollend` (`scrollRatio < 0.1`) early-close heuristics SHALL be removed
- **AND** the CE SHALL NOT set `pointer-events: none` on `.scroll-area` to prevent bounce-back
- **NOTE** These heuristics and the pointer-events lock are unnecessary under the scroll-to-closed-stop + `IntersectionObserver` model: the dismiss is the scroll itself and no premature `close()`/`hidePopover()` is committed mid-gesture, so there is nothing to lock against. (Title retained for spec-delta continuity; behavior is the removal of the heuristic.)

#### Scenario: Dismiss detection ignores programmatic and initial-snap scroll
- **WHEN** the sheet opens and the `initial-snap` sequence (or any programmatic scroll) momentarily rests the scroll position on the dismiss zone before settling on `.sheet-body`
- **THEN** the CE SHALL NOT dismiss the sheet
- **AND** dismiss SHALL be honored only once the sheet has settled on `.sheet-body` and the sheet body subsequently leaves the viewport (guarded by the just-opened guard)
- **NOTE** This prevents the iOS/WebKit "flash then close" defect, where the programmatic re-snap trace (scroll ratio `1 → 0`) was previously misread as a user swipe-to-dismiss by scroll-ratio heuristics.

#### Scenario: Fallback dismiss detection where scrollsnapchange is unsupported
- **WHEN** the engine does not support `scrollsnapchange` (e.g., Firefox)
- **THEN** dismiss detection SHALL still function unchanged, because the `IntersectionObserver` (not `scrollsnapchange`) is the single primary detection mechanism across all engines
- **AND** no `scrollend`/`pointerup` scroll-ratio fallback SHALL be required
- **NOTE** By making `IntersectionObserver` the primary path rather than a fallback, the CE removes the engine-specific detection branching that previously distinguished Chromium (`scrollsnapchange`) from other engines.

#### Scenario: Just-opened dismiss guard
- **WHEN** the sheet has just been opened (during the open transition / before it has settled on `.sheet-body`)
- **THEN** the CE SHALL suppress any dismiss signal, so the sheet cannot close itself before the user interacts
- **AND** the guard SHALL release once the sheet has settled on `.sheet-body`

#### Scenario: Bounce-back prevention after dismiss-zone snap
- **WHEN** the user begins a swipe-down dismiss and then reverses direction (scrolls the sheet back up) before it leaves the viewport
- **THEN** the sheet SHALL settle back to `.sheet-body` and remain open, with no `hidePopover()` call and no `sheet-closed` event
- **AND** after a genuine dismiss, a subsequent upward page scroll SHALL NOT cause the sheet to reappear
- **AND** the CE SHALL achieve this WITHOUT setting `pointer-events: none` on `.scroll-area`
- **NOTE** Because no `close()` is committed mid-gesture and there is no separate opacity/`overlay` fade competing with the scroll, reversing the gesture is honored as ordinary direct manipulation rather than being overridden — eliminating the prior bounce-back defect. (Title retained for spec-delta continuity; the mechanism changes from a pointer-events lock to not committing a premature close.)

#### Scenario: Close animation completes within 160ms
- **WHEN** the sheet is dismissed by any mechanism (swipe, tap-outside, ESC, Android back, programmatic)
- **THEN** the visible close SHALL be the scroll of `.scroll-area` to the closed snap stop, coupled with the scroll-driven backdrop fade
- **AND** `hidePopover()` SHALL be called only after the `IntersectionObserver` confirms the sheet body has left the viewport, so the slide-out is fully visible
- **AND** the CE SHALL NOT rely on a fixed-duration opacity/`overlay allow-discrete` fade decoupled from the scroll to perform the close
- **NOTE** Title retained for spec-delta continuity; the close is now the dismiss scroll (native momentum, honoring `prefers-reduced-motion`), not a fixed 160ms fade. The prior 160ms `--_duration` fade is removed.

#### Scenario: Tap-outside dismiss
- **WHEN** the sheet is open and `dismissable` is `true`
- **AND** the user taps/clicks the dimmed area above the sheet body (the `.dismiss-zone`)
- **THEN** the CE SHALL scroll to the closed snap stop, and on the resulting off-screen detection set `open` to `false`, call `hidePopover()`, and dispatch `sheet-closed`
- **NOTE** Tap-outside is implemented as a `click` handler on the `.dismiss-zone` element. Native popover light-dismiss is intentionally disabled by using `popover="manual"` (auto light-dismiss would also fire mid-swipe). Under full-viewport coverage the sheet-body occludes most of the surface, so the explicit `.dismiss-zone` click handler is the reliable tap-outside path.
- **WHEN** `dismissable` is `false`
- **THEN** the `.dismiss-zone` tap SHALL NOT close the sheet

#### Scenario: Gesture-coupled backdrop fade
- **WHEN** the browser supports scroll-driven animations (`@supports (animation-timeline: scroll())`)
- **THEN** the `::backdrop` opacity (and its blur) SHALL be driven by the `.scroll-area` scroll position via `animation-timeline: scroll()`, so the backdrop fades as the user swipes the sheet toward the dismiss zone and is fully cleared by the dismiss threshold
- **WHEN** the browser does NOT support scroll-driven animations (e.g., Firefox)
- **THEN** the `::backdrop` SHALL fall back to an opacity `transition` on open/close (the prior behavior)

#### Scenario: Non-dismissable mode
- **WHEN** `dismissable` is `false`
- **THEN** the popover SHALL be opened with `showPopover()` and the CE SHALL keep the background `inert` for the sheet's whole lifetime (modal-like blocking)
- **AND** the CE SHALL suppress the Escape close request (the `keydown` Escape handler SHALL NOT close it), and there SHALL be no tap-outside close
- **AND** `.scroll-area` SHALL have `data-dismissable="false"`
- **AND** the dismiss zone SHALL remain in the DOM with `aria-hidden="true"` (required for the `initial-snap` animation pattern)
- **AND** CSS SHALL set `.dismiss-zone` to `scroll-snap-align: none` and `pointer-events: none` via `.scroll-area:not([data-dismissable="true"]) .dismiss-zone`
- **AND** `.sheet-body` SHALL be the only active snap target, ensuring the sheet body is visible on open

#### Scenario: Dismissable mode with close-request dismiss (ESC / Android back)
- **WHEN** `dismissable` is `true` (default)
- **THEN** pressing Escape (desktop) SHALL close the sheet, handled by a CE `keydown` listener (a `popover="manual"` does not emit a native `cancel`/close request), which SHALL initiate the scroll-to-closed-stop dismiss
- **AND** the Android back gesture/button SHALL close the sheet via the consumer's `popstate` handling (history-driven), which sets `open` to `false` and triggers the programmatic close path
- **AND** each SHALL result in `open` being set to `false` and a `sheet-closed` event being dispatched

#### Scenario: Close animation completes within 160ms (legacy duration removed)
- **WHEN** `prefers-reduced-motion: reduce` is NOT active
- **THEN** the dismiss scroll SHALL use `scroll-behavior: smooth` for the slide-out
- **WHEN** `prefers-reduced-motion: reduce` is active
- **THEN** the close SHALL resolve instantly (jump-scroll), with no smooth animation
- **NOTE** This scenario documents the replacement of the fixed 160ms `--_duration` close fade; the perceived close latency is now bounded by the native smooth-scroll settle, not a CSS transition duration.

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
- **AND** `max-block-size` SHALL be `90svh`
- **AND** overflow-y SHALL be `auto` for scrollable content
- **AND** `contain` SHALL be `layout` (layout containment boundary — see layout stability scenario)

#### Scenario: Slotted content
- **WHEN** content is placed inside `<bottom-sheet>`
- **THEN** it SHALL be projected via `<au-slot>` into the sheet body below the handle bar

#### Scenario: Focus management
- **WHEN** the sheet opens
- **THEN** the CE SHALL move focus into the sheet body and trap it there while open (CE-managed, since `popover` provides no native focus trap)
- **WHEN** the sheet closes
- **THEN** focus SHALL return to the element that was focused before the sheet opened

#### Scenario: History integration
- **WHEN** the sheet opens
- **THEN** a history entry SHALL NOT be pushed by the CE itself
- **AND** consuming components MAY manage history state independently via `open` binding

#### Scenario: Reduced motion
- **WHEN** `prefers-reduced-motion: reduce` is active
- **THEN** the open/close SHALL resolve to an instant (or near-instant) transition with no smooth dismiss scroll animation
- **AND** the scroll-driven backdrop fade SHALL likewise resolve to an instant open/close

#### Scenario: Detach cleanup
- **WHEN** the CE is detached from the DOM while the sheet is open
- **THEN** all event listeners and observers (`.dismiss-zone` click, the Escape `keydown` listener, and the `IntersectionObserver`) SHALL be removed / disconnected
- **AND** `hidePopover()` SHALL be called on the popover
- **AND** any background `inert` applied by the CE SHALL be removed
- **AND** no memory leaks SHALL occur

