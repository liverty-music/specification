## ADDED Requirements

### Requirement: Onboarding Step State Management

The system SHALL maintain an `onboardingStep` numeric value in LocalStorage under the key `liverty:onboardingStep` to track the user's progress through the linear tutorial. Valid values are 0-6 (in-progress) and 7 (COMPLETED).

#### Scenario: Initial state for new visitor

- **WHEN** a user visits the application for the first time
- **AND** no `liverty:onboardingStep` key exists in LocalStorage
- **THEN** the system SHALL treat the user as a new visitor at Step 0

#### Scenario: Step progression persists across page reloads

- **WHEN** a user progresses to Step N during the tutorial
- **THEN** the system SHALL write `N` to `liverty:onboardingStep` in LocalStorage
- **AND** on page reload, the system SHALL restore the user to Step N

#### Scenario: Step value is corrupted or invalid

- **WHEN** the `liverty:onboardingStep` value is not a valid number between 0-7
- **THEN** the system SHALL treat the user as a new visitor at Step 0
- **AND** the system SHALL overwrite the invalid value

### Requirement: Linear Step Progression

The system SHALL enforce a strict linear progression through tutorial steps. Users SHALL NOT be able to skip steps or navigate freely during the tutorial.

#### Scenario: Step 0 - Landing Page entry

- **WHEN** a user is at Step 0 (LP)
- **AND** the user taps the [Get Started] CTA
- **THEN** the system SHALL advance `onboardingStep` to 1
- **AND** navigate to the Artist Discovery screen

#### Scenario: Step 1 - Artist Discovery completion

- **WHEN** a user is at Step 1 (Artist Discovery / Bubble UI)
- **AND** the user has followed 3 or more artists via bubble taps
- **THEN** the system SHALL activate and highlight the [Generate Dashboard] CTA button at the bottom of the screen
- **AND** when the user taps the CTA, the system SHALL advance `onboardingStep` to 3 (DASHBOARD), skipping Step 2 (LOADING)
- **AND** the system SHALL navigate directly to the Dashboard (`/dashboard`)

#### Scenario: Step 1 - Progress bar display

- **WHEN** a user is at Step 1
- **THEN** the system SHALL display a progress bar showing the count of followed artists (e.g., "1/3", "2/3", "3/3")
- **AND** the progress bar target SHALL be 3 artists
- **AND** the user MAY continue following more artists after reaching 3

#### Scenario: Step 2 - Loading sequence (deprecated for onboarding)

- **WHEN** a user is at Step 2 (LOADING)
- **THEN** this step is no longer entered during the onboarding flow
- **AND** the `OnboardingStep.LOADING` enum value (2) SHALL be retained for backward compatibility with existing localStorage state
- **AND** if a user has `onboardingStep=2` in localStorage from a prior session, the route guard SHALL redirect them to the Dashboard (`/dashboard`)

#### Scenario: Step 3 - Dashboard reveal with region selection

- **WHEN** a user is at Step 3 (Dashboard)
- **THEN** the system SHALL display the region selection BottomSheet overlay
- **AND** after region selection, the system SHALL display the Live Highway UI
- **AND** the system SHALL disable scrolling
- **AND** the system SHALL apply a spotlight overlay highlighting only the first concert card
- **AND** the system SHALL display a coach mark tooltip: "Found it! Tap the card to see details."

#### Scenario: Step 3 - Concert card tap

- **WHEN** a user is at Step 3
- **AND** the user taps the spotlighted concert card
- **THEN** the system SHALL advance `onboardingStep` to 4
- **AND** open the concert detail BottomSheet

#### Scenario: Step 4 - Detail BottomSheet with My Artists tab guidance

- **WHEN** a user is at Step 4 (Detail BottomSheet)
- **THEN** the system SHALL NOT allow the BottomSheet to be dismissed (no swipe-down, no backdrop tap)
- **AND** the system SHALL highlight the [My Artists] tab in the bottom navigation
- **AND** the system SHALL display a coach mark tooltip: "Customize notifications from the artist screen."

#### Scenario: Step 4 - My Artists tab tap

- **WHEN** a user is at Step 4
- **AND** the user taps the highlighted [My Artists] tab
- **THEN** the system SHALL advance `onboardingStep` to 5
- **AND** navigate to the My Artists screen

#### Scenario: Step 5 - Passion Level guidance

- **WHEN** a user is at Step 5 (My Artists)
- **THEN** the system SHALL highlight the Passion Level toggle of the first artist in the list
- **AND** the system SHALL display a coach mark tooltip: "Set to Must Go if you'd travel anywhere for this artist."

#### Scenario: Step 5 - Passion Level changed

- **WHEN** a user is at Step 5
- **AND** the user changes the Passion Level of the highlighted artist
- **THEN** the system SHALL display a brief explanation of the notification control system (e.g., "Must Go: notified for all events nationwide. Local Only: events in your area only.")
- **AND** the system SHALL advance `onboardingStep` to 6

#### Scenario: Step 6 - SignUp modal display

- **WHEN** a user is at Step 6
- **THEN** the system SHALL display the Passkey authentication modal
- **AND** the modal SHALL NOT be dismissible (no close button, no backdrop tap, no escape key)
- **AND** the modal message SHALL read: "All set! Create an account to save your preferences and never miss a live show."

#### Scenario: Step 6 - Passkey authentication success

- **WHEN** a user is at Step 6
- **AND** the user completes Passkey authentication successfully
- **THEN** the system SHALL trigger the guest data merge process
- **AND** upon merge completion, set `onboardingStep` to 7 (COMPLETED)
- **AND** remove all tutorial UI restrictions (coach marks, spotlight, interaction locks)
- **AND** navigate to the Dashboard with full unrestricted access

#### Scenario: Step 6 - Page reload

- **WHEN** a user reloads the page with `onboardingStep = 6`
- **THEN** the system SHALL re-display the non-dismissible SignUp modal immediately

### Requirement: Coach Mark Overlay System

The system SHALL provide a reusable coach mark overlay component that highlights a target element with a spotlight effect and displays instructional text.

#### Scenario: Spotlight renders for active step

- **WHEN** a tutorial step requires a coach mark
- **THEN** the system SHALL dim the entire screen with a semi-transparent overlay
- **AND** the system SHALL cut out a highlight area around the target element
- **AND** the system SHALL display a tooltip with the step's instructional text

#### Scenario: Only highlighted element is interactive

- **WHEN** the coach mark overlay is active
- **THEN** only the highlighted target element SHALL accept user interaction (tap/click)
- **AND** all other elements SHALL be blocked by the overlay

#### Scenario: Coach mark target not found

- **WHEN** the target element for a coach mark is not present in the DOM
- **THEN** the system SHALL retry finding the element with exponential backoff (up to 5 seconds)
- **AND** if still not found, the system SHALL display an error message and allow the user to retry the step

### Requirement: Authentication Overrides Tutorial

The system SHALL treat `isAuthenticated = true` as an unconditional override of all tutorial restrictions, regardless of the `onboardingStep` value.

#### Scenario: Authenticated user with onboardingStep = 0

- **WHEN** a user has `isAuthenticated = true`
- **AND** `onboardingStep` is 0 or unset (e.g., new device)
- **THEN** the system SHALL grant full unrestricted access to the Dashboard
- **AND** the system SHALL NOT display any tutorial UI

#### Scenario: Authenticated user with onboardingStep = 3

- **WHEN** a user has `isAuthenticated = true`
- **AND** `onboardingStep` is 3
- **THEN** the system SHALL grant full unrestricted access to the Dashboard
- **AND** the system SHALL NOT display coach marks or spotlight overlays
