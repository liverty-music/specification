## ADDED Requirements

### Requirement: Popover guide on discover page entry during onboarding
The system SHALL display a one-time popover guide when an onboarding user navigates to the discover page, using the native Popover API with `popover="auto"` for light-dismiss behavior.

#### Scenario: Popover appears on onboarding entry
- **WHEN** `OnboardingService.isOnboarding` is `true` and the user navigates to `/discover`
- **THEN** the system SHALL call `showPopover()` on the guide element immediately upon component attachment
- **AND** the popover SHALL display a message explaining the interaction (e.g., "ライブ情報を追いかけたいアーティストをタップしてフォローしよう")
- **AND** the popover SHALL render in the top layer, outside the grid flow

#### Scenario: Popover dismissed via light-dismiss
- **WHEN** the popover is visible and the user taps outside the popover
- **THEN** the popover SHALL close via the browser's native light-dismiss mechanism
- **AND** no additional JavaScript dismiss handler SHALL be required

#### Scenario: Popover entry animation uses CSS only
- **WHEN** the popover opens
- **THEN** the popover SHALL animate from `opacity: 0; translate: 0 1rem` to `opacity: 1; translate: 0 0` using `@starting-style` and `:popover-open`
- **AND** the transition SHALL use `transition-behavior: allow-discrete` for `display` and `overlay` properties
- **AND** only compositor-thread properties (`opacity`, `translate`) SHALL be animated

#### Scenario: Popover exit animation
- **WHEN** the popover is dismissed
- **THEN** the popover SHALL animate from `opacity: 1; translate: 0 0` to `opacity: 0; translate: 0 1rem`
- **AND** the `display` transition SHALL keep the element visible during the exit animation

#### Scenario: Non-onboarding user does not see popover
- **WHEN** `OnboardingService.isOnboarding` is `false` and the user navigates to `/discover`
- **THEN** the popover element SHALL NOT be rendered in the DOM
- **AND** `showPopover()` SHALL NOT be called

#### Scenario: Popover shown only once per onboarding session
- **WHEN** the user dismisses the popover and continues using the discover page
- **THEN** the popover SHALL NOT reappear during the same page visit
- **AND** if the user navigates away and returns to `/discover` while still onboarding, the popover MAY appear again (no cross-navigation persistence required)

#### Scenario: Respects prefers-reduced-motion
- **WHEN** the user has `prefers-reduced-motion: reduce` enabled
- **THEN** the popover SHALL appear and disappear instantly without transition animations
