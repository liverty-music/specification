# Onboarding Tutorial

## Purpose

Defines the linear onboarding tutorial flow that guides new users through artist discovery, dashboard interaction, and account creation.
## Requirements
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

#### Scenario: Step 1 - Artist Discovery completion with concert data gate

- **WHEN** a user is at Step 1 (Artist Discovery / Bubble UI)
- **AND** the user has followed 3 or more artists via bubble taps
- **AND** concert search results have been received for all followed artists (or timed out after 15 seconds per artist)
- **THEN** the system SHALL activate a coach mark spotlight on the Dashboard icon in the bottom navigation bar (target: `[data-nav-dashboard]`)
- **AND** the coach mark SHALL display the message: "タイムテーブルを見てみよう！"
- **AND** when the user taps the Dashboard icon, the system SHALL advance `onboardingStep` to 3 (DASHBOARD), skipping Step 2 (LOADING)
- **AND** the system SHALL navigate to the Dashboard (`/dashboard`)

#### Scenario: Step 1 - Progress bar display

- **WHEN** a user is at Step 1
- **THEN** the system SHALL display a progress bar showing concert search completion status
- **AND** the progress bar SHALL fill continuously based on the ratio of completed concert searches to total followed artists
- **AND** the progress bar target SHALL require 3 or more artists with completed (or timed-out) concert searches
- **AND** the user MAY continue following more artists after reaching 3

#### Scenario: Step 2 - Loading sequence (deprecated for onboarding)

- **WHEN** a user is at Step 2 (LOADING)
- **THEN** this step is no longer entered during the onboarding flow
- **AND** the `OnboardingStep.LOADING` enum value (2) SHALL be retained for backward compatibility with existing localStorage state
- **AND** if a user has `onboardingStep=2` in localStorage from a prior session, the route guard SHALL redirect them to the Dashboard (`/dashboard`)

#### Scenario: Step 3 - Dashboard reveal with celebration and lane introduction

- **WHEN** a user is at Step 3 (Dashboard)
- **THEN** the system SHALL display the celebration overlay (see `onboarding-celebration` capability)
- **AND** after celebration, the system SHALL display the region selection BottomSheet overlay (if home area not yet set)
- **AND** after region selection, the system SHALL run the lane introduction sequence (see `dashboard-lane-introduction` capability)
- **AND** after lane introduction, the system SHALL disable scrolling
- **AND** the system SHALL apply a spotlight overlay highlighting only the first concert card
- **AND** the system SHALL display a coach mark tooltip: "タップして詳細を見てみよう！"

#### Scenario: Step 3 - Concert card tap

- **WHEN** a user is at Step 3
- **AND** the user taps the spotlighted concert card
- **THEN** the system SHALL advance `onboardingStep` to 4
- **AND** open the concert detail sheet (popover with `popover="manual"`)

#### Scenario: Step 4 - Detail sheet with My Artists tab guidance

- **WHEN** a user is at Step 4 (Detail sheet open)
- **THEN** the system SHALL NOT allow the detail sheet to be dismissed (no swipe-down, no backdrop tap)
- **AND** the system SHALL highlight the [My Artists] tab in the bottom navigation bar
- **AND** the system SHALL display a coach mark tooltip: "アーティスト一覧も見てみよう！"
- **AND** the coach mark popover SHALL re-enter the top layer AFTER the detail sheet popover has been shown, ensuring the coach mark renders above the detail sheet per LIFO stacking rules

#### Scenario: Step 4 - My Artists tab tap

- **WHEN** a user is at Step 4
- **AND** the user taps the highlighted [My Artists] tab
- **THEN** the system SHALL advance `onboardingStep` to 5
- **AND** navigate to the My Artists screen

#### Scenario: Step 5 - Passion Level guidance

- **WHEN** a user is at Step 5 (My Artists)
- **THEN** the system SHALL highlight the Passion Level toggle of the first artist in the list
- **AND** the system SHALL display a coach mark tooltip: "好きなレベルを設定してみよう！"

#### Scenario: Step 5 - Passion Level changed

See "Requirement: Step 5 Passion Level Explanation Timing" below for the updated behaviour of this scenario.

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

The system SHALL provide a reusable coach mark overlay component that highlights a target element with a high-contrast spotlight effect, pulse animation, and large instructional tooltip.

#### Scenario: Spotlight renders for active step

- **WHEN** a tutorial step requires a coach mark
- **THEN** the system SHALL dim the entire screen with a semi-transparent overlay at `oklch(0% 0 0deg / 75%)`
- **AND** the system SHALL cut out a highlight area around the target element
- **AND** the highlight area SHALL have a `2px solid` ring in the brand accent color
- **AND** the ring SHALL animate with a pulse effect (scale 1→1.05→1, 1.5s infinite)
- **AND** the system SHALL display a tooltip with the step's instructional text
- **AND** the tooltip SHALL use `font-size: 16px`, `padding: 16px`, brand accent background color, white text, and `border-radius: 12px`

#### Scenario: Only highlighted element is interactive

- **WHEN** the coach mark overlay is active
- **THEN** only the highlighted target element SHALL accept user interaction (tap/click)
- **AND** all other elements SHALL be blocked by the overlay

#### Scenario: Scroll lock during coach mark

- **WHEN** the coach mark overlay is active
- **THEN** the system SHALL disable scrolling on the `<au-viewport>` scroll container by adding `overflow: hidden`
- **AND** scrolling SHALL be restored when the coach mark is deactivated

#### Scenario: Coach mark target not found

- **WHEN** the target element for a coach mark is not present in the DOM
- **THEN** the system SHALL retry finding the element with exponential backoff (up to 5 seconds)
- **AND** if still not found, the system SHALL display an error message and allow the user to retry the step

#### Scenario: Reduced motion preference

- **WHEN** the user has `prefers-reduced-motion: reduce` enabled
- **THEN** the spotlight pulse animation SHALL be disabled
- **AND** the static ring border SHALL remain visible

#### Scenario: Bring to front for top-layer re-ordering

- **WHEN** the coach mark needs to appear above another popover already in the top layer (e.g., the concert detail sheet at Step 4)
- **THEN** the coach mark SHALL call `hidePopover()` followed by `showPopover()` on its overlay element to re-enter the top layer at the LIFO top position
- **AND** the re-show SHALL be batched within a single animation frame to avoid visual flicker

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

---

### Requirement: No Permission Prompts During Onboarding Steps 1-6

The system SHALL suppress all permission prompts (PWA install banner, push notification opt-in) while the user is progressing through onboarding Steps 1-6. Permission prompts are deferred until after Step 7 (COMPLETED).

#### Scenario: PWA install suppressed during tutorial

- **WHEN** the user is at any onboarding step between 1 and 6
- **AND** the browser fires the `beforeinstallprompt` event
- **THEN** the system SHALL capture the event for later use
- **BUT** the system SHALL NOT display the PWA install banner

#### Scenario: Notification prompt suppressed during tutorial

- **WHEN** the user is at any onboarding step between 1 and 6
- **THEN** the system SHALL NOT render or evaluate the notification prompt component

#### Scenario: Prompts become eligible after completion

- **WHEN** the user completes Step 6 and transitions to Step 7 (COMPLETED)
- **THEN** permission prompts SHALL become eligible according to the prompt-timing capability rules
- **AND** the onboarding tutorial SHALL NOT block prompt display after this point

---

### Requirement: Step 5 Passion Level Explanation Timing

The Step 5 passion explanation SHALL provide immediate visual feedback on tap and appear after a shorter delay, replacing the current 3-second silent wait.

#### Scenario: Step 5 - Passion Level changed (MODIFIED)

- **WHEN** a user is at Step 5
- **AND** the user changes the Passion Level of the highlighted artist
- **THEN** the passion button SHALL immediately show a brief highlight/pulse animation (scale 1 -> 1.1 -> 1, ~300ms) as visual confirmation that the selection registered
- **AND** the system SHALL display the passion explanation after an 800ms delay (not 3000ms)
- **AND** the system SHALL advance `onboardingStep` to 6

---

### Requirement: Sign-up Modal Entrance Animation

The sign-up modal (Step 6) SHALL animate on entrance to match the visual polish of the onboarding flow.

#### Scenario: Sign-up modal entrance

- **WHEN** the sign-up modal becomes visible (Step 6 activation or page reload at Step 6)
- **THEN** the modal content panel SHALL animate in with a scale + fade effect (scale 0.95 -> 1, opacity 0 -> 1)
- **AND** the animation duration SHALL be 400ms with cubic-bezier spring easing
- **AND** a subtle radial gradient glow SHALL appear behind the modal content using the brand-primary color at low opacity

#### Scenario: Reduced motion preference

- **WHEN** the user has `prefers-reduced-motion: reduce` enabled
- **THEN** the sign-up modal entrance animation SHALL be skipped
- **AND** the modal SHALL appear instantly, with both the entrance animation and the `::before` radial gradient glow suppressed (`display: none`; the glow is a static pseudo-element not covered by `animation: none`)

