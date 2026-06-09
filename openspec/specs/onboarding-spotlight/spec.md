# Onboarding Spotlight

## Purpose

Defines the coach mark spotlight overlay — the visual cutout, tooltip, target-click delegation, and lifecycle. The coach mark is a single, transient, non-blocking hint owned by `CoachMarkService`.
## Requirements
### Requirement: Spotlight Visual Layer via Box-Shadow

The coach mark spotlight SHALL use a CSS Anchor Positioning hybrid approach. A `.visual-spotlight` element SHALL be positioned over the target using `anchor()` functions in `inset` properties, with `box-shadow: 0 0 0 100vmax` to create the dark overlay and a transparent cutout. The element SHALL use `border-radius: var(--spotlight-radius)` for shape control and `pointer-events: none` to allow click-through.

#### Scenario: Spotlight renders with rounded cutout over target

- **WHEN** a coach mark is activated with a target selector
- **THEN** the system SHALL position a `.visual-spotlight` element using CSS `anchor()` functions referencing the target's anchor name
- **AND** the spotlight SHALL create a dark overlay (70% opacity) across the entire viewport via `box-shadow: 0 0 0 100vmax`
- **AND** the spotlight cutout SHALL match the target's border-radius via `var(--spotlight-radius)`
- **AND** the spotlight element SHALL have `pointer-events: none`

#### Scenario: Spotlight shape adapts per step

- **WHEN** the coach mark targets a circular element (e.g., nav icon)
- **THEN** `--spotlight-radius` SHALL be set to `50%`
- **WHEN** the coach mark targets a rectangular element (e.g., concert card)
- **THEN** `--spotlight-radius` SHALL be set to `12px`

#### Scenario: Spotlight cutout has padding around target

- **WHEN** the spotlight is positioned over a target element
- **THEN** the spotlight cutout SHALL extend 8px beyond the target's bounding box on all sides (via `margin: -8px`)

### Requirement: Coach Mark Overlay System

The system SHALL provide a reusable coach mark overlay component that highlights a target element as a non-blocking hint. Coach mark state (target selector, message, radius, active flag, and `onTap` callback) SHALL be owned by a dedicated `CoachMarkService`, not by `OnboardingService`. The `aria-label` on the tooltip SHALL be `"Onboarding tip"`. Navigation SHALL be delegated to the target element's native click behavior; the coach mark SHALL NOT call `router.load()`. The `onTap` callback SHALL NOT advance any onboarding step (there is no step machine); it MAY perform incidental non-navigation side effects only. Target selectors SHALL be scoped to a specific component context (e.g., `concert-highway [data-stage="home"]`) to prevent matching elements in unrelated components.

#### Scenario: Spotlight renders for active coach mark

- **WHEN** a coach mark is activated via `CoachMarkService`
- **THEN** the system SHALL display the spotlight overlay with instructional text
- **AND** the tooltip `aria-label` SHALL be `"Onboarding tip"`

#### Scenario: Nav tab tap through spotlight delegates to href

- **WHEN** a coach mark spotlight is active on a nav tab element
- **AND** the user taps the spotlighted element
- **THEN** the system SHALL call `currentTarget.click()` to fire the element's native click event
- **AND** the system SHALL call the `onTap?.()` callback (for incidental side effects only, never step advancement)
- **AND** the system SHALL NOT call `router.load()` from within the coach mark component or its `onTap` callback

#### Scenario: Off-target interaction is allowed (non-blocking)

- **WHEN** a coach mark spotlight is active
- **AND** the user taps or scrolls an area outside the highlighted target
- **THEN** the interaction SHALL reach the underlying page (no click-blocker interception)
- **AND** page scroll SHALL remain enabled

#### Scenario: Target selector is scoped to component context

- **WHEN** `CoachMarkService.activate()` is called with a target selector
- **THEN** the selector SHALL include a component-scoped prefix (e.g., `concert-highway [data-stage="home"]` instead of bare `[data-stage="home"]`)
- **AND** `document.querySelector()` SHALL NOT match elements in unrelated components (e.g., `page-help` decorative labels)

### Requirement: Spotlight Uses Popover Top Layer

The coach mark overlay container SHALL use `popover="manual"` to render on the browser's top layer, eliminating z-index stacking context issues.

#### Scenario: Spotlight renders above all page content

- **WHEN** the coach mark is activated
- **THEN** the overlay container SHALL call `showPopover()` to enter the top layer
- **AND** the spotlight SHALL render above all other content regardless of z-index

#### Scenario: Popover UA styles are neutralized

- **WHEN** the popover is displayed
- **THEN** the container SHALL have `background: transparent`, `border: none`, `padding: 0`, `margin: 0`
- **AND** `::backdrop` SHALL be set to `display: none`

### Requirement: Route Detach Spotlight Cleanup

When a route hosting an active coach mark detaches (user navigates away), the spotlight SHALL be deactivated via the `detaching()` lifecycle hook to prevent orphaned View Transitions and popover state. Note: `unloading()` (router lifecycle) is also a valid placement since it runs earlier in the navigation sequence (`canUnload → canLoad → unloading → loading → detaching`), but `detaching()` is chosen for consistency with existing cleanup code (AbortController, timers, scroll listeners) already in this hook.

#### Scenario: Route detaching cleans up spotlight
- **WHEN** the host route's `detaching()` lifecycle hook fires
- **THEN** `CoachMarkService.deactivate()` SHALL be called
- **AND** any in-progress View Transition SHALL be safely terminated

#### Scenario: Navigation during active spotlight does not throw
- **WHEN** the spotlight is active with a View Transition in progress
- **AND** the user navigates to another route (via nav tab, browser back, or coach mark tap)
- **THEN** the route transition SHALL complete without throwing "Transition was aborted because of invalid state"
- **AND** no unhandled promise rejection SHALL be emitted

### Requirement: Coach Mark Target Click Delegates Navigation to Aurelia Router

The coach mark's `target-interceptor` div overlays the actual target element. When the user taps the interceptor, it programmatically calls `currentTarget.click()` on the real target element. For navigation targets (e.g., `<a>` with `href`), this `.click()` triggers Aurelia Router's `href` intercept, which handles the route transition declaratively. The `onTap` callback SHALL only perform incidental application side effects (never onboarding step advancement, which no longer exists) and SHALL never call imperative `router.load()`.

#### Scenario: Nav link target navigates via Aurelia Router href intercept
- **WHEN** the coach mark target is a navigation link (e.g., `<a data-nav="home" href="dashboard">`)
- **AND** the user taps the `target-interceptor` overlay
- **THEN** `currentTarget.click()` SHALL fire on the `<a>` element
- **AND** Aurelia Router's `useHref` intercept SHALL handle the resulting click event as a declarative route transition
- **AND** the `onTap` callback SHALL NOT advance any onboarding step
- **AND** `router.load()` SHALL NOT be called imperatively from the `onTap` callback

#### Scenario: Non-nav target triggers onTap callback for application logic
- **WHEN** the coach mark target is a non-navigation element (e.g., concert card)
- **AND** the user taps the `target-interceptor` overlay
- **THEN** `currentTarget.click()` SHALL fire on the target element, triggering its bound event handlers
- **AND** the `onTap` callback SHALL be invoked for incidental application logic only (e.g., opening a detail sheet), never onboarding step advancement

### Requirement: Smooth Spotlight Movement via View Transitions API

The spotlight SHALL animate smoothly when moving between targets, both within the same page (e.g., lane introduction sequence) and across route navigations (e.g., Discovery → Dashboard → My Artists). The `.visual-spotlight` element SHALL use `view-transition-name: spotlight` to enable browser-native cross-fade/slide animation.

#### Scenario: Same-page target change (lane introduction)

- **WHEN** the spotlight target changes within the same page (e.g., HOME STAGE → NEAR STAGE → AWAY STAGE → concert card)
- **THEN** the system SHALL wrap the anchor-name reassignment in `document.startViewTransition()`
- **AND** the spotlight SHALL slide smoothly from the old target position to the new target position
- **AND** the animation duration SHALL be approximately 400ms with an ease-out curve

#### Scenario: Cross-route target change

- **WHEN** a route navigation occurs while the spotlight is active (e.g., Discovery Dashboard icon → Dashboard lane header, or Dashboard My Artists tab → My Artists Passion Level)
- **THEN** the system SHALL use `document.startViewTransition()` to wrap the navigation
- **AND** the spotlight SHALL animate from its previous position to the new target on the destination page
- **AND** the tooltip text SHALL update to the new step's message
- **AND** the popover SHALL NOT be closed during the transition

#### Scenario: Reduced motion preference

- **WHEN** the user has `prefers-reduced-motion: reduce` enabled
- **THEN** the View Transition animation SHALL be suppressed (instant position change)
- **AND** the spotlight SHALL still appear at the correct target position

### Requirement: Tooltip Anchor Positioning

The coach mark tooltip SHALL be positioned using CSS Anchor Positioning relative to the target element.

#### Scenario: Tooltip appears below target

- **WHEN** the coach mark is active
- **THEN** the tooltip SHALL use `position-anchor` referencing the target's anchor name
- **AND** the tooltip SHALL use `position-area: block-end` as the default placement
- **AND** the tooltip SHALL use `position-try-fallbacks: flip-block, flip-inline` for overflow handling

### Requirement: Tooltip Visual Treatment

The coach mark tooltip SHALL render with a transparent background, allowing the handwritten text to float directly on the dark overlay.

#### Scenario: Tooltip renders without solid background

- **WHEN** the coach mark tooltip is displayed
- **THEN** `.coach-mark-tooltip` SHALL have `background: transparent`
- **AND** `.coach-mark-tooltip` SHALL have `filter: none` (no drop-shadow)
- **AND** the tooltip text color SHALL remain `var(--color-white)`
- **AND** the font SHALL remain `var(--coach-font-handwritten)` ("Klee One", cursive)
- **AND** the tooltip SHALL be visually readable against the 70% black overlay

### Requirement: Inline SVG Directional Arrow

The tooltip SHALL include a hand-drawn style directional arrow rendered as inline SVG. No external image assets (`<img>`, `.png`, `.svg` files) SHALL be used. The arrow SHALL visually connect the tooltip to the spotlight target.

#### Scenario: Arrow direction adapts to tooltip placement

- **WHEN** the tooltip is positioned below the target (`position-area: block-end`)
- **THEN** the arrow SVG SHALL render an upward-pointing curved path connecting from the tooltip toward the target
- **WHEN** the tooltip is positioned above the target (via `position-try-fallbacks: flip-block`)
- **THEN** the arrow SVG SHALL render a downward-pointing curved path
- **AND** the arrow direction SHALL be selected using Aurelia `switch.bind` on the resolved `position-area`

#### Scenario: Arrow drawing animation on appearance

- **WHEN** the tooltip first appears or the target changes
- **THEN** the arrow path SHALL animate with a drawing effect using `stroke-dasharray` / `stroke-dashoffset` over approximately 600ms
- **AND** the arrowhead SHALL fade in after the line drawing completes (300ms delay)

#### Scenario: Arrow inherits theme color

- **WHEN** the tooltip is rendered
- **THEN** the SVG SHALL use `stroke="currentColor"` to inherit the tooltip's text color
- **AND** the arrow SHALL automatically adapt to theme changes without separate assets

#### Scenario: Arrow with reduced motion preference

- **WHEN** the user has `prefers-reduced-motion: reduce` enabled
- **THEN** the drawing animation SHALL be disabled (arrow appears immediately)
- **AND** the arrow SHALL still be visible in its final drawn state

### Requirement: Handwritten Font for Tooltip Text

The coach mark tooltip message text SHALL use a handwritten-style font to reinforce the personal, friendly tone of the onboarding guidance. The font SHALL support Japanese characters since all tooltip messages are in Japanese.

#### Scenario: Tooltip message renders in handwritten font

- **WHEN** the coach mark tooltip is displayed
- **THEN** the tooltip message text SHALL use a Japanese-compatible handwritten font (e.g., `Klee One`, `Zen Kurenaido`)
- **AND** the font SHALL be loaded from Google Fonts
- **AND** the font SHALL be applied only to the tooltip message element, not to action buttons or other UI elements

#### Scenario: Handwritten font fallback

- **WHEN** the handwritten font fails to load (e.g., offline, network error)
- **THEN** the tooltip message SHALL fall back to `cursive` generic font family
- **AND** the tooltip SHALL remain readable and functional

#### Scenario: Handwritten font with reduced motion preference

- **WHEN** the user has `prefers-reduced-motion: reduce` enabled
- **THEN** the handwritten font SHALL still be applied (it is a visual style, not an animation)

### Requirement: Invisible Target Rejection

The `findAndHighlight()` method SHALL reject target elements that are invisible (zero dimensions) and continue retry logic as if the element was not found.

#### Scenario: Zero-dimension target is skipped

- **WHEN** `document.querySelector(targetSelector)` returns an element
- **AND** the element has zero width and zero height (`getBoundingClientRect()` returns 0×0)
- **THEN** the system SHALL treat the element as not found
- **AND** the system SHALL continue exponential backoff retry logic

#### Scenario: Hidden element in closed popover is skipped

- **WHEN** a matching element exists inside a closed popover or `display: none` container
- **AND** the element's bounding rect has zero dimensions
- **THEN** the system SHALL skip this element
- **AND** the system SHALL retry until a visible matching element appears or timeout is reached

### Requirement: Single Transient Non-Blocking Coach Mark

With the step machine removed, the coach mark SHALL be a single, transient, non-blocking hint rather than a multi-step blocking overlay. At most one coach mark SHALL be active at a time. It SHALL NOT lock page scroll and SHALL NOT block interaction with the rest of the page; it visually highlights its target and lets the user keep using the app. State and lifecycle are owned by `CoachMarkService` (`activate` / `deactivate`), and the `<coach-mark>` component SHALL be placed once at the app-shell level, driven by `CoachMarkService` (target selector, message, radius, active flag, `onTap`). The coach mark SHALL be dismissed when the user taps its target or when the host route detaches.

#### Scenario: Coach mark does not block the rest of the page

- **WHEN** a coach mark is active
- **THEN** the page outside the highlighted target SHALL remain interactive (no full-viewport click-blockers)
- **AND** page scroll SHALL NOT be locked (`<au-viewport>` `overflow` SHALL NOT be forced to `hidden`)
- **AND** the dashboard is reachable at any time, consistent with the soft gate

#### Scenario: Single coach mark driven from the app shell

- **WHEN** the coach mark is active
- **THEN** the `<coach-mark>` component SHALL be rendered once in the app shell, not in individual route templates
- **AND** `CoachMarkService` SHALL drive its target selector, message, spotlight radius, and active state
- **AND** no more than one coach mark SHALL be active simultaneously

#### Scenario: Coach mark dismissed on tap or route detach

- **WHEN** the user taps the coach mark target, OR the host route's `detaching()` lifecycle hook fires
- **THEN** `CoachMarkService.deactivate()` SHALL be called
- **AND** the spotlight, tooltip, and any anchor-name SHALL be fully cleaned up

## Test Cases

### Unit Tests (Vitest — coach-mark.spec.ts)

#### TC-SP-01: Target element receives anchor-name when highlighted

- **Given** a coach mark component is created
- **When** `activateSpotlight(selector, message, onTap)` is called with a valid target selector
- **Then** the target element's `anchorName` style SHALL be set to `--coach-target`

#### TC-SP-02: Popover opens only once (continuous persistence)

- **Given** the coach mark is not yet visible
- **When** `activateSpotlight()` is called for the first time
- **Then** `showPopover()` SHALL be called once on the overlay element
- **When** `activateSpotlight()` is called again with a different target
- **Then** `showPopover()` SHALL NOT be called again

#### TC-SP-03: Target change does not close popover

- **Given** the coach mark is active with target A
- **When** `activateSpotlight()` is called with target B
- **Then** `hidePopover()` SHALL NOT be called
- **And** target A's `anchorName` SHALL be cleared
- **And** target B's `anchorName` SHALL be set to `--coach-target`

#### TC-SP-04: Deactivate cleans up all state

- **Given** the coach mark is active
- **When** `deactivateSpotlight()` is called
- **Then** `hidePopover()` SHALL be called on the overlay element
- **And** the current target's `anchorName` SHALL be cleared
- **And** scroll lock on `<au-viewport>` SHALL be released (`overflow` reset)

#### TC-SP-05: Arrow direction resolves to 'up' or 'down'

- **Given** the coach mark is active
- **When** the tooltip position is `block-end` (below target)
- **Then** `arrowDirection` SHALL be `'up'`
- **When** the tooltip position is `block-start` (above target)
- **Then** `arrowDirection` SHALL be `'down'`

#### TC-SP-06: Blocker click invokes onTap callback

- **Given** the coach mark is active with an `onTap` callback
- **When** the user clicks a `.click-blocker` element
- **Then** the `onTap` callback SHALL be invoked

#### TC-SP-07: spotlightRadius defaults to '12px'

- **Given** the coach mark is activated without specifying spotlightRadius
- **Then** the `--spotlight-radius` CSS custom property SHALL default to `'12px'`

#### TC-SP-08: Target retry with exponential backoff

- **Given** the target element does not exist in the DOM
- **When** `activateSpotlight()` is called
- **Then** the system SHALL retry finding the target (using fake timers to advance)
- **And** the system SHALL find and highlight the target once it appears

#### TC-SP-09: Target interceptor intercepts clicks

- **Given** the coach mark is active with a target
- **When** the user clicks the `.target-interceptor` overlay
- **Then** `preventDefault()` and `stopPropagation()` SHALL be called on the event
- **And** the `onTap` callback SHALL be invoked

### E2E Tests (Playwright — manual verification)

#### TC-SP-E2E-01: Full onboarding spotlight continuity

- Verify spotlight opens at Step 1 and persists through Step 5 without blinking
- Verify View Transition slide animation between targets
- Verify tooltip text updates at each step
- Verify cleanup at Step 6: no anchor-name, no scroll lock, popover hidden
