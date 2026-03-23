## MODIFIED Requirements

### Requirement: Bottom Sheet Custom Element
The system SHALL provide a `<bottom-sheet>` custom element as the single dialog primitive for all overlay content, using the Popover API with CSS scroll-snap dismiss.

#### Scenario: Basic open/close via bindable
- **WHEN** `<bottom-sheet open.bind="isOpen">` has `open` set to `true`
- **THEN** the CE SHALL call `showPopover()` on the internal `<dialog>` element
- **AND** the CE SHALL defer `scrollTo({ top: scrollHeight })` by one animation frame (`requestAnimationFrame`) to ensure the browser has completed top-layer layout before programmatic scroll
- **AND** the sheet-body SHALL be visible at the bottom of the viewport after the deferred scroll
- **WHEN** `open` is set to `false`
- **THEN** the CE SHALL call `hidePopover()` and the sheet SHALL animate out

#### Scenario: Scroll-snap dismiss
- **WHEN** the sheet is open and `dismissable` is `true`
- **THEN** a dismiss zone SHALL be rendered above the sheet content as a direct child of the `dialog` element
- **AND** swiping down (physical gesture: finger moves downward, scrollTop decreases) SHALL scroll toward the dismiss zone at the top, triggering close on `scrollend`
- **AND** the `::backdrop` opacity SHALL track scroll progress via CSS Scroll-Driven Animations (`scroll-timeline` on `dialog`, `animation-timeline` on `dialog::backdrop`)
- **AND** if the browser does not support Scroll-Driven Animations on `::backdrop`, the backdrop SHALL display at static full opacity as a fallback

#### Scenario: DOM structure
- **WHEN** the sheet is rendered
- **THEN** the internal DOM SHALL be `dialog > .dismiss-zone + .sheet-body`
- **AND** the `.dismiss-zone` SHALL be the first child (`scroll-snap-align: start`) at the top of the scroll container
- **AND** the `.sheet-body` SHALL be the last child (`scroll-snap-align: end`) at the bottom of the scroll container
- **AND** the `dialog` element itself SHALL be the scroll-snap container (`overflow-y: auto`, `scroll-snap-type: y mandatory`)
- **AND** no intermediate `.scroll-wrapper` or `.sheet-page` wrapper SHALL exist

#### Scenario: Swipe-down dismiss detection
- **WHEN** the user swipes down (finger moves downward), decreasing scrollTop toward the dismiss zone
- **AND** the `scrollend` event fires
- **THEN** the CE SHALL check if `scrollRatio < 0.1` (scrolled near the top where the dismiss zone is)
- **AND** if so, the CE SHALL set `open` to `false` and dispatch `sheet-closed`
