## ADDED Requirements

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

## MODIFIED Requirements

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

## REMOVED Requirements

### Requirement: Click-Blocker Layer via Transparent Anchor-Positioned Divs

**Reason**: The coach mark is now a non-blocking hint (see "Single Transient Non-Blocking Coach Mark"). Blocking all off-target interaction and locking scroll contradicts the soft gate, under which the dashboard and every route remain reachable at any time.

**Migration**: Remove the four `.mask-top` / `.mask-right` / `.mask-bottom` / `.mask-left` click-blocker divs and the `<au-viewport>` scroll lock from the coach mark component. The spotlight remains a visual-only cutout (`pointer-events: none`); tapping the target still delegates to its native click. Off-target taps reach the page.

### Requirement: Continuous Spotlight Persistence

**Reason**: This requirement is built entirely on the deleted linear step machine — a single overlay that persists from "Step 1" through "Step 6", reassigning anchor-names as `onboardingStep` advances, with a scroll lock released "at Step 6". With onboarding reduced to a single `isOnboarding` boolean and a single transient coach mark on the discovery page, there is no multi-step persistence to maintain.

**Migration**: Remove the persist-across-steps behavior, the `onboardingStep`-driven anchor-name reassignment, the Step-6 `hidePopover()`/scroll-lock-release path, and the app-shell placement scenario's dependency on `OnboardingService`. Single-coach-mark placement, app-shell rendering, and detach cleanup are now defined by "Single Transient Non-Blocking Coach Mark"; the empty-selector guard and retry-timer cancellation in `findAndHighlight()` move with the coach-mark component into `CoachMarkService`.
