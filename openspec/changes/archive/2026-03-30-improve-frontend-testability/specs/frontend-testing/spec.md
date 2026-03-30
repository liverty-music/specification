## ADDED Requirements

### Requirement: Dashboard route manages lane introduction state machine
The `DashboardRoute` SHALL manage the lane introduction onboarding flow as a pure state machine testable without a real DOM, with nav-dimming delegated to `INavDimmingService` and localStorage access delegated to `ILocalStorage`.

#### Scenario: loading() sets needsRegion for authenticated user without home
- **WHEN** `loading()` is called and `userService.current.home` is falsy
- **THEN** `needsRegion` SHALL be `true`

#### Scenario: loading() sets showSignupBanner for completed-onboarding guest
- **WHEN** `loading()` is called and the user is unauthenticated and `onboarding.isCompleted` is `true`
- **THEN** `showSignupBanner` SHALL be `true`

#### Scenario: attached() starts lane intro when onboarding step is DASHBOARD
- **WHEN** `attached()` is called and `onboarding.currentStep === OnboardingStep.DASHBOARD`
- **THEN** `INavDimmingService.setDimmed(true)` SHALL be called and `laneIntroPhase` SHALL be `'home'`

#### Scenario: attached() shows post-signup dialog when flag is pending
- **WHEN** `attached()` is called and `ILocalStorage.getItem(StorageKeys.postSignupShown)` returns `'pending'`
- **THEN** `showPostSignupDialog` SHALL be `true` and `removeItem` SHALL be called for that key

#### Scenario: advanceLaneIntro progresses through phases
- **WHEN** `onLaneIntroTap()` is called with `laneIntroPhase === 'home'`
- **THEN** `laneIntroPhase` SHALL advance to `'near'`
- **WHEN** called again
- **THEN** `laneIntroPhase` SHALL advance to `'away'`
- **WHEN** called again
- **THEN** `completeLaneIntro()` SHALL be triggered

#### Scenario: completeLaneIntro shows celebration when not yet shown
- **WHEN** `completeLaneIntro()` is called and `ILocalStorage.getItem(StorageKeys.celebrationShown)` returns `null`
- **THEN** `showCelebration` SHALL be `true` and `ILocalStorage.setItem(StorageKeys.celebrationShown, '1')` SHALL be called

#### Scenario: completeLaneIntro undims nav when celebration already shown
- **WHEN** `completeLaneIntro()` is called and `celebrationShown` is `true`
- **THEN** `showCelebration` SHALL remain `false` and `INavDimmingService.setDimmed(false)` SHALL be called

#### Scenario: onCelebrationDismissed undims nav and deactivates spotlight
- **WHEN** `onCelebrationDismissed()` is called
- **THEN** `showCelebration` SHALL be `false`, `INavDimmingService.setDimmed(false)` SHALL be called, and `onboarding.deactivateSpotlight()` SHALL be called

#### Scenario: detaching clears abort controller and undims nav
- **WHEN** `detaching()` is called
- **THEN** the abort controller SHALL be aborted and `INavDimmingService.setDimmed(false)` SHALL be called

### Requirement: Mock helpers cover INavDimmingService and ILocalStorage
The test helper library SHALL provide typed mock factories for the new injectable services introduced by this change.

#### Scenario: createMockNavDimmingService returns spy
- **WHEN** `createMockNavDimmingService()` is called
- **THEN** it SHALL return an object with `setDimmed` as a Vitest spy

#### Scenario: createMockLocalStorage returns configurable spy
- **WHEN** `createMockLocalStorage(initialData)` is called with an initial key-value map
- **THEN** it SHALL return an object implementing `ILocalStorage` with `getItem`, `setItem`, `removeItem` as Vitest spies that read/write the initial data

## MODIFIED Requirements

### Requirement: Coverage reporting is configured
Vitest SHALL be configured with V8 coverage reporting with raised thresholds reflecting the expanded test suite.

#### Scenario: Running tests with coverage
- **WHEN** `vitest --coverage` is executed
- **THEN** a coverage report SHALL be generated showing statement, branch, and function coverage

#### Scenario: Coverage thresholds enforce minimum levels
- **WHEN** coverage falls below thresholds (statements: 70%, branches: 78%, functions: 70%, lines: 70%)
- **THEN** the coverage check SHALL fail
