## ADDED Requirements

### Requirement: Route Detach Spotlight Cleanup

When the dashboard route detaches (user navigates away), the spotlight SHALL be deactivated via the `detaching()` lifecycle hook to prevent orphaned View Transitions and popover state. Note: `unloading()` (router lifecycle) is also a valid placement since it runs earlier in the navigation sequence (`canUnload → canLoad → unloading → loading → detaching`), but `detaching()` is chosen for consistency with existing cleanup code (AbortController, timers, scroll listeners) already in this hook.

#### Scenario: Dashboard detaching cleans up spotlight
- **WHEN** the dashboard route's `detaching()` lifecycle hook fires
- **THEN** `onboardingService.deactivateSpotlight()` SHALL be called
- **AND** any in-progress View Transition SHALL be safely terminated
- **AND** the scroll lock on `<au-viewport>` SHALL be released

#### Scenario: Navigation during active spotlight does not throw
- **WHEN** the spotlight is active with a View Transition in progress
- **AND** the user navigates to another route (via nav tab, browser back, or coach mark tap)
- **THEN** the route transition SHALL complete without throwing "Transition was aborted because of invalid state"
- **AND** no unhandled promise rejection SHALL be emitted

### Requirement: Coach Mark Target Click Delegates Navigation to Aurelia Router

The coach mark's `target-interceptor` div overlays the actual target element. When the user taps the interceptor, it programmatically calls `currentTarget.click()` on the real target element. For navigation targets (e.g., `<a>` with `href`), this `.click()` triggers Aurelia Router's `href` intercept, which handles the route transition declaratively. The `onTap` callback SHALL only perform state updates (e.g., `setStep`), never imperative `router.load()`.

#### Scenario: Nav link target navigates via Aurelia Router href intercept
- **WHEN** the coach mark target is a navigation link (e.g., `<a data-nav="my-artists" href="my-artists">`)
- **AND** the user taps the `target-interceptor` overlay
- **THEN** `currentTarget.click()` SHALL fire on the `<a>` element
- **AND** Aurelia Router's `useHref` intercept SHALL handle the resulting click event as a declarative route transition
- **AND** the `onTap` callback SHALL only update onboarding state (e.g., `onboardingService.setStep()`)
- **AND** `router.load()` SHALL NOT be called imperatively from the `onTap` callback

#### Scenario: Non-nav target triggers onTap callback for application logic
- **WHEN** the coach mark target is a non-navigation element (e.g., concert card)
- **AND** the user taps the `target-interceptor` overlay
- **THEN** `currentTarget.click()` SHALL fire on the target element, triggering its bound event handlers
- **AND** the `onTap` callback SHALL be invoked for additional application logic (e.g., advancing onboarding step, opening detail sheet)

## MODIFIED Requirements

### Requirement: Continuous Spotlight Persistence

The spotlight SHALL remain continuously active from the moment it first appears (Step 1, Dashboard icon) until the sign-up modal is displayed (Step 6). The popover SHALL NOT be closed and reopened between steps; instead, the target SHALL be updated via anchor-name reassignment while the overlay remains open. This provides uninterrupted visual guidance throughout the entire onboarding tutorial. **Exception**: the Step 1→3 transition (Discovery → Dashboard) SHALL deactivate and reactivate the spotlight — the popover must be cleared before navigation so that Dashboard overlays (celebration, region selector) render above the top layer without being blocked by click-blockers (see `onboarding-tutorial`, "Step 1 - Spotlight deactivation before navigation"). **Additionally**, route components with active spotlights SHALL call `deactivateSpotlight()` in their `detaching()` lifecycle hook to ensure cleanup regardless of navigation trigger.

The `findAndHighlight()` method SHALL validate `targetSelector` before calling `querySelector`. When `targetSelector` is empty or falsy, the method SHALL return immediately without calling `querySelector` or initiating retry logic. This prevents `InvalidSelectorError` caused by non-deterministic Aurelia binding update order when multiple Store properties change simultaneously.

The `findAndHighlight()` method SHALL cancel any pending retry timer before starting a new retry chain. This prevents timer leaks when `targetSelectorChanged` fires while a previous retry is still running (e.g., during the lane introduction sequence where phases advance every 2 seconds but retry chains run up to 5 seconds).

#### Scenario: Spotlight activates at Step 1 and persists through Step 5
- **WHEN** the coach mark first activates at Step 1 (Dashboard icon in discover page)
- **THEN** the overlay popover SHALL call `showPopover()` once
- **AND** the popover SHALL remain open through all subsequent steps (Step 3 lane intro, Step 3 card, Step 4 My Artists tab, Step 5 Passion Level)
- **AND** the target SHALL change by reassigning `anchor-name` to the new target element
- **AND** the tooltip message SHALL update to match the current step

#### Scenario: Spotlight deactivates at Step 6
- **WHEN** `onboardingStep` advances to 6 (SignUp)
- **THEN** the overlay popover SHALL call `hidePopover()`
- **AND** the current target's `anchor-name` SHALL be cleared
- **AND** the scroll lock on `<au-viewport>` SHALL be released (`overflow` reset)
- **AND** no orphaned click-blockers or anchor-names SHALL remain in the DOM

#### Scenario: Route detach triggers deactivation
- **WHEN** a route containing an active spotlight detaches
- **THEN** `deactivateSpotlight()` SHALL be called in the `detaching()` lifecycle hook
- **AND** the spotlight state SHALL be fully cleaned up before the new route attaches
