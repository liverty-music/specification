## MODIFIED Requirements

### Requirement: Continuous Spotlight Persistence

The spotlight SHALL remain continuously active from the moment it first appears (Step 1, Dashboard icon) until the sign-up modal is displayed (Step 6). The popover SHALL NOT be closed and reopened between steps; instead, the target SHALL be updated via anchor-name reassignment while the overlay remains open. This provides uninterrupted visual guidance throughout the entire onboarding tutorial. **Exception**: the Step 1→3 transition (Discovery → Dashboard) SHALL deactivate and reactivate the spotlight — the popover must be cleared before navigation so that Dashboard overlays (celebration, region selector) render above the top layer without being blocked by click-blockers (see `onboarding-tutorial`, "Step 1 - Spotlight deactivation before navigation").

The `findAndHighlight()` method SHALL validate `targetSelector` before calling `querySelector`. When `targetSelector` is empty or falsy, the method SHALL return immediately without calling `querySelector` or initiating retry logic. This prevents `InvalidSelectorError` caused by non-deterministic Aurelia binding update order when multiple Store properties change simultaneously.

#### Scenario: Spotlight activates at Step 1 and persists through Step 5

- **WHEN** the coach mark first activates at Step 1 (Dashboard icon in discover page)
- **THEN** the overlay popover SHALL call `showPopover()` once
- **AND** the popover SHALL remain open through all subsequent steps (Step 3 lane intro, Step 3 card, Step 4 My Artists tab, Step 5 Passion Level)
- **AND** the target SHALL change by reassigning `anchor-name` to the new target element
- **AND** the tooltip message SHALL update to match the current step

#### Scenario: Spotlight deactivates at Step 6

- **WHEN** `onboardingStep` advances to 6 (SignUp)
- **THEN** the overlay popover SHALL call `hidePopover()`
- **AND** the current target's `anchor-name` SHALL be removed
- **AND** the scroll lock on `<au-viewport>` SHALL be released
- **AND** no orphaned click-blockers or anchor-names SHALL remain in the DOM

#### Scenario: App-shell level placement

- **WHEN** the onboarding spotlight is active
- **THEN** the `<coach-mark>` component SHALL be rendered in the app shell (`my-app.html`), not in individual route page templates
- **AND** the onboarding service SHALL drive the target selector, message, spotlight radius, and active state
- **AND** individual route pages SHALL NOT contain their own `<coach-mark>` instances for onboarding steps

#### Scenario: Empty target selector is safely ignored

- **WHEN** the `targetSelector` bindable property is set to an empty string (e.g., via Store `clearSpotlight` dispatch)
- **AND** `targetSelectorChanged()` fires before `activeChanged()` due to non-deterministic binding update order
- **THEN** `findAndHighlight()` SHALL return immediately without calling `document.querySelector`
- **AND** no `InvalidSelectorError` SHALL be thrown
- **AND** no retry timer SHALL be started
