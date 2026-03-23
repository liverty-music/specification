## MODIFIED Requirements

### Requirement: Bottom Sheet Custom Element
The system SHALL provide a `<bottom-sheet>` custom element as the single dialog primitive for all overlay content, using the Popover API with CSS scroll-snap dismiss.

#### Scenario: Basic open/close via bindable
- **WHEN** `<bottom-sheet open.bind="isOpen">` has `open` set to `true`
- **THEN** the CE SHALL call `showPopover()` on the internal `<dialog>` element
- **AND** the sheet-body SHALL be visible at the bottom of the viewport via CSS scroll-snap initial positioning (no JavaScript scroll manipulation)
- **WHEN** `open` is set to `false`
- **THEN** the CE SHALL call `hidePopover()` and the sheet SHALL animate out

#### Scenario: CSS-only initial scroll position via Snappy Scroll-Start
- **WHEN** the dialog popover transitions from hidden to visible
- **THEN** the CE SHALL use a CSS `@keyframes` animation that temporarily sets `--snap-align: none` on all snap points except the sheet-body
- **AND** the sheet-body SHALL retain `scroll-snap-align: end` during the animation, causing the browser's native re-snap mechanism to position the scroll container at the sheet-body
- **AND** after the animation completes, the dismiss-zone SHALL regain `scroll-snap-align: start` to enable swipe-to-dismiss
- **AND** no JavaScript `scrollTo()`, `scrollTop`, or `requestAnimationFrame` SHALL be used for initial positioning

#### Scenario: DOM structure
- **WHEN** the sheet is rendered
- **THEN** the internal DOM SHALL be `dialog > .dismiss-zone + .sheet-body`
- **AND** the `.dismiss-zone` SHALL always be present in the DOM regardless of the `dismissable` property
- **AND** the `.dismiss-zone` SHALL be the first child at the top of the scroll container
- **AND** the `.sheet-body` SHALL be the last child at the bottom of the scroll container
- **AND** the `dialog` element itself SHALL be the scroll-snap container (`overflow-y: auto`, `scroll-snap-type: y mandatory`)
- **AND** no intermediate wrapper elements SHALL exist
- **AND** no `if.bind` or conditional rendering SHALL control the dismiss-zone's DOM presence

#### Scenario: Non-dismissable mode
- **WHEN** `dismissable` is `false`
- **THEN** the CE SHALL use `popover="manual"`
- **AND** the dismiss-zone SHALL remain in the DOM but with `scroll-snap-align: none` (controlled via CSS attribute selector)
- **AND** the dismiss-zone SHALL have `pointer-events: none`
- **AND** ESC key SHALL NOT close the sheet
- **AND** the sheet-body SHALL be visible at the bottom of the viewport (same as dismissable mode)

#### Scenario: Swipe-down dismiss detection
- **WHEN** the user swipes down (finger moves downward), decreasing scrollTop toward the dismiss zone
- **AND** the `scrollend` event fires
- **AND** `dismissable` is `true`
- **THEN** the CE SHALL check if `scrollRatio < 0.1` (scrolled near the top where the dismiss zone is)
- **AND** if so, the CE SHALL set `open` to `false` and dispatch `sheet-closed`
