## ADDED Requirements

### Requirement: FAB Visible After Onboarding Completion

The system SHALL display a persistent PWA install FAB in the bottom-right corner of the screen, anchored above the Nav Bar, once onboarding is completed — regardless of authentication state.

#### Scenario: Guest user completes onboarding

- **WHEN** the user completes the onboarding flow (`OnboardingStep.COMPLETED`)
- **AND** the user is not authenticated
- **AND** the app has not been installed
- **THEN** the system SHALL display the PWA install FAB

#### Scenario: Authenticated user completes onboarding

- **WHEN** the user completes the onboarding flow
- **AND** the user is authenticated
- **AND** the app has not been installed
- **THEN** the system SHALL display the PWA install FAB

#### Scenario: FAB not shown during onboarding

- **WHEN** the user is in any active onboarding step (DISCOVERY, DASHBOARD, MY_ARTISTS)
- **THEN** the system SHALL NOT display the PWA install FAB

---

### Requirement: FAB Install Behavior by Platform

The FAB SHALL trigger the appropriate install flow based on the user's platform.

#### Scenario: Android/Chrome — native install prompt

- **WHEN** the user taps the FAB
- **AND** the browser has fired `beforeinstallprompt`
- **THEN** the system SHALL call `deferredPrompt.prompt()`
- **AND** the native browser install dialog SHALL appear

#### Scenario: iOS Safari — instruction sheet

- **WHEN** the user taps the FAB
- **AND** the browser has NOT fired `beforeinstallprompt` (iOS Safari)
- **THEN** the system SHALL open a `bottom-sheet` component
- **AND** the sheet SHALL display step-by-step instructions:
  1. Safari の共有ボタン（□↑）をタップ
  2.「ホーム画面に追加」を選択
  3.「追加」をタップ
- **AND** the sheet SHALL provide a single dismiss action (閉じる)

#### Scenario: iOS instruction sheet dismissed

- **WHEN** the user taps 閉じる on the iOS instruction sheet
- **THEN** the sheet SHALL close
- **AND** the FAB SHALL remain visible

---

### Requirement: FAB Disappears After Installation

The system SHALL remove the FAB permanently once the app is installed.

#### Scenario: App installed via FAB

- **WHEN** the browser fires the `appinstalled` event
- **THEN** the system SHALL hide the FAB
- **AND** the FAB SHALL NOT reappear in subsequent sessions

#### Scenario: App already installed on load

- **WHEN** the app loads
- **AND** `navigator.standalone` is `true` (iOS) OR the display mode matches `standalone` (Android)
- **THEN** the system SHALL NOT display the FAB

---

### Requirement: FAB Entry Animation

The FAB SHALL animate on first appearance to draw user attention, then remain static.

#### Scenario: First appearance animation

- **WHEN** the FAB becomes visible for the first time in a session
- **THEN** the system SHALL animate the FAB sliding up from below (`translateY(150%) → translateY(0)`, 400ms ease-out)
- **AND** after the slide completes, a ripple ring SHALL animate outward and fade exactly 2 times, then stop
- **AND** the idle state SHALL show a brand gradient glow via `box-shadow` (no looping animation)

#### Scenario: Reduced motion

- **WHEN** `prefers-reduced-motion: reduce` is set
- **THEN** the system SHALL replace the slide-up and ripple with a simple `opacity: 0 → 1` fade

#### Scenario: Tap feedback

- **WHEN** the user taps the FAB
- **THEN** the FAB SHALL briefly scale down (`scale(0.92)` for 50ms) then return to `scale(1)` over 100ms

---

### Requirement: FAB Position When signup-prompt-banner Is Visible

When the `signup-prompt-banner` is displayed, the FAB SHALL be overlaid on the banner's button row in the right-side whitespace.

#### Scenario: Both FAB and signup-banner visible

- **WHEN** the FAB is visible
- **AND** the `signup-prompt-banner` is visible
- **THEN** the FAB SHALL be positioned in the right whitespace of the banner's button row
- **AND** the FAB SHALL NOT obscure the "アカウント作成" button or the banner's dismiss button
- **AND** both elements SHALL maintain a minimum 44px touch target

#### Scenario: Only FAB visible (no banner)

- **WHEN** the FAB is visible
- **AND** the `signup-prompt-banner` is not visible
- **THEN** the FAB SHALL be positioned above the Nav Bar with `inset-inline-end: var(--space-s)` and `inset-block-end: calc(3.5rem + env(safe-area-inset-bottom, 0px) + var(--space-s))`
