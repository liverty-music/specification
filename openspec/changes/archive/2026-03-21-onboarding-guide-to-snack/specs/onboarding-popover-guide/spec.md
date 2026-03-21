## MODIFIED Requirements

### Requirement: Popover guide on discover page entry during onboarding
The system SHALL display a one-time instructional snack notification when an onboarding user navigates to the discover page, using the existing snack-bar component with auto-dismiss behavior.

#### Scenario: Snack notification appears on onboarding entry
- **WHEN** `OnboardingService.isOnboarding` is `true` and the user navigates to `/discover`
- **THEN** the system SHALL publish a `Snack` event via `IEventAggregator` in the `attached()` lifecycle
- **AND** the snack SHALL have `severity: 'info'` and `duration: 5000`
- **AND** the snack SHALL display the localized message from `discovery.popoverGuide`
- **AND** the snack SHALL render at the top of the viewport via the global `<snack-bar>` component

#### Scenario: Snack auto-dismisses after duration
- **WHEN** the snack is visible and 5000 ms have elapsed
- **THEN** the snack SHALL auto-dismiss via the snack-bar's built-in timer
- **AND** no explicit user action SHALL be required to dismiss the notification

#### Scenario: Non-onboarding user does not see snack
- **WHEN** `OnboardingService.isOnboarding` is `false` and the user navigates to `/discover`
- **THEN** no `Snack` event SHALL be published
- **AND** no onboarding notification SHALL appear

#### Scenario: Snack shown only once per page visit
- **WHEN** the snack has been published and the user remains on `/discover`
- **THEN** the snack SHALL NOT be published again during the same page visit
- **AND** if the user navigates away and returns to `/discover` while still onboarding, the snack MAY appear again

## REMOVED Requirements

### Requirement: Popover dismissed via light-dismiss
**Reason**: Replaced by snack-bar auto-dismiss. The snack-bar uses `popover="manual"` with timer-based dismissal instead of `popover="auto"` light-dismiss.
**Migration**: Remove `<dialog popover="auto">` element and `.onboarding-guide` CSS from `discovery-route`. The snack-bar handles display and dismissal.

### Requirement: Popover entry animation uses CSS only
**Reason**: The snack-bar component provides its own entry/exit animations. Custom CSS animations for the popover guide are no longer needed.
**Migration**: Remove `.onboarding-guide` CSS block (~50 lines including `@starting-style`, `:popover-open`, and backdrop rules) from `discovery-route.css`.

### Requirement: Popover exit animation
**Reason**: Handled by snack-bar's built-in exit transition.
**Migration**: No action needed — removed with the `.onboarding-guide` CSS block.

### Requirement: Respects prefers-reduced-motion
**Reason**: The snack-bar component handles reduced-motion preferences in its own CSS.
**Migration**: No action needed — the snack-bar's existing reduced-motion handling applies.
