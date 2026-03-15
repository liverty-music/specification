## MODIFIED Requirements

### Requirement: Coach Mark Overlay System

The system SHALL provide a reusable coach mark overlay component that highlights a target element using a CSS Anchor Positioning hybrid approach: a visual spotlight layer (box-shadow with border-radius) for the dark overlay cutout and transparent click-blocker divs for interaction control. The component SHALL render on the browser's top layer via the Popover API.

#### Scenario: Spotlight renders for active step

- **WHEN** a tutorial step requires a coach mark
- **THEN** the system SHALL display a `.visual-spotlight` element with `box-shadow: 0 0 0 100vmax` creating a 70% opacity dark overlay
- **AND** the spotlight cutout SHALL match the target's shape via `border-radius: var(--spotlight-radius)`
- **AND** the spotlight SHALL have a `2px solid` ring in the brand accent color
- **AND** the ring SHALL animate with a pulse effect (scale 1 -> 1.05 -> 1, 1.5s infinite)
- **AND** the system SHALL display a tooltip with the step's instructional text
- **AND** the tooltip message text SHALL use a handwritten font (`Klee One`, fallback: `cursive`)
- **AND** the tooltip SHALL use `font-size: 18px`, `padding: 16px`, white text on a transparent background with a subtle `drop-shadow` for legibility over the dark overlay
- **AND** the tooltip arrow SHALL be positioned relative to the text based on direction: above the text when pointing up (tooltip below target), below the text when pointing down (tooltip above target)

#### Scenario: Only highlighted element is interactive

- **WHEN** the coach mark overlay is active
- **THEN** four transparent click-blocker divs (top, right, bottom, left) SHALL be positioned using CSS `anchor()` functions to cover the viewport outside the target bounds
- **AND** the click-blockers SHALL have `pointer-events: auto` to block taps
- **AND** the spotlight cutout area SHALL have `pointer-events: none` allowing taps to pass through to the target
- **AND** the target element SHALL receive click events natively without JS coordinate forwarding

#### Scenario: Scroll lock during coach mark

- **WHEN** the coach mark overlay is active
- **THEN** the system SHALL disable scrolling on the `<au-viewport>` scroll container by adding `overflow: hidden`
- **AND** scrolling SHALL be restored when the coach mark is deactivated

#### Scenario: Coach mark target not found

- **WHEN** the target element for a coach mark is not present in the DOM
- **THEN** the system SHALL retry finding the element with exponential backoff (up to 5 seconds)
- **AND** if still not found, the system SHALL log an error and hide the coach mark

#### Scenario: Reduced motion preference

- **WHEN** the user has `prefers-reduced-motion: reduce` enabled
- **THEN** the spotlight pulse animation SHALL be disabled
- **AND** the static ring border SHALL remain visible

### Requirement: Linear Step Progression

The system SHALL enforce a strict linear progression through tutorial steps. Users SHALL NOT be able to skip steps or navigate freely during the tutorial. Direct navigation via the bottom nav bar SHALL advance the step when the prerequisite conditions are met.

#### Scenario: Step 0 - Landing Page entry

- **WHEN** a user is at Step 0 (LP)
- **AND** the user taps the [Get Started] CTA
- **THEN** the system SHALL advance `onboardingStep` to 1
- **AND** navigate to the Artist Discovery screen

#### Scenario: Step 1 - Artist Discovery completion with concert data gate

- **WHEN** a user is at Step 1 (Artist Discovery / Bubble UI)
- **AND** the user has followed 3 or more artists via bubble taps
- **AND** concert search results have been received for all followed artists (or timed out after 15 seconds per artist)
- **THEN** the system SHALL activate the continuous spotlight on the Dashboard icon in the bottom navigation bar (target: `[data-nav-dashboard]`)
- **AND** the spotlight SHALL remain continuously active from this point through Step 5 (see `onboarding-spotlight` capability, Continuous Spotlight Persistence)
- **AND** the coach mark SHALL display the message: "タイムテーブルを見てみよう！"
- **AND** when the user taps the Dashboard icon through the spotlight, the system SHALL advance `onboardingStep` to 3 (DASHBOARD), skipping Step 2 (LOADING)
- **AND** the system SHALL navigate to the Dashboard (`/dashboard`)
- **AND** the spotlight SHALL slide smoothly to the next target on the Dashboard via View Transitions API

#### Scenario: Step 1 - Direct Home nav tap when coach mark is active

- **WHEN** a user is at Step 1
- **AND** the coach mark spotlight on the Dashboard icon is active
- **AND** the user taps the Home/Dashboard icon in the bottom nav bar (bypassing the coach mark overlay)
- **THEN** the system SHALL advance `onboardingStep` to 3 (DASHBOARD)
- **AND** the system SHALL navigate to `/dashboard`

#### Scenario: Step 2 - Loading sequence (deprecated for onboarding)

- **WHEN** a user is at Step 2 (LOADING)
- **THEN** this step is no longer entered during the onboarding flow
- **AND** the `OnboardingStep.LOADING` enum value (2) SHALL be retained for backward compatibility with existing localStorage state
- **AND** if a user has `onboardingStep=2` in localStorage from a prior session, the route guard SHALL redirect them to the Dashboard (`/dashboard`)

#### Scenario: Step 1 - Spotlight deactivation before navigation

- **WHEN** a user is at Step 1
- **AND** the user taps the Dashboard coach mark
- **THEN** the system SHALL deactivate the spotlight (`deactivateSpotlight()`) before navigating to `/dashboard`
- **AND** this ensures the popover top layer is cleared so that Dashboard overlays (celebration, region selector) are not blocked by click-blockers
- **AND** the Dashboard SHALL reactivate the spotlight during the lane introduction sequence (see Step 3 scenario below)

#### Scenario: Step 3 - Dashboard reveal with celebration and lane introduction

- **WHEN** a user is at Step 3 (Dashboard)
- **THEN** the system SHALL display the celebration overlay only once per onboarding session, persisted via `localStorage` key `onboarding.celebrationShown`
- **AND** on page reload, if `celebrationShown` is already set, the celebration SHALL NOT replay
- **AND** after celebration (or immediately if already shown), the system SHALL display the region selection BottomSheet overlay (if home area not yet set)
- **AND** after region selection, the system SHALL run the lane introduction sequence (see `dashboard-lane-introduction` capability)
- **AND** during lane introduction, the continuous spotlight SHALL slide between lane headers (HOME STAGE → NEAR STAGE → AWAY STAGE) via View Transitions API
- **AND** after lane introduction, the system SHALL disable scrolling
- **AND** the spotlight SHALL slide to the first concert card
- **AND** the system SHALL display a coach mark tooltip: "タップして詳細を見てみよう！"

#### Scenario: Step 3 - Concert card tap

- **WHEN** a user is at Step 3
- **AND** the user taps the spotlighted concert card
- **THEN** the system SHALL advance `onboardingStep` to 4
- **AND** open the concert detail sheet (popover)
- **AND** the spotlight SHALL slide to the [My Artists] tab in the bottom navigation bar

#### Scenario: Step 4 - Detail sheet with My Artists tab guidance

- **WHEN** a user is at Step 4 (Detail sheet open)
- **THEN** the system SHALL NOT allow the detail sheet to be dismissed (no swipe-down, no backdrop tap)
- **AND** the spotlight SHALL already be highlighting the [My Artists] tab (slid from concert card)
- **AND** the system SHALL display a coach mark tooltip: "アーティスト一覧も見てみよう！"

#### Scenario: Step 4 - My Artists tab tap

- **WHEN** a user is at Step 4
- **AND** the user taps the highlighted [My Artists] tab
- **THEN** the system SHALL advance `onboardingStep` to 5
- **AND** navigate to the My Artists screen
- **AND** the spotlight SHALL slide to the Passion Level toggle of the first artist via View Transitions API

#### Scenario: Step 5 - Passion Level guidance

- **WHEN** a user is at Step 5 (My Artists)
- **THEN** the spotlight SHALL already be highlighting the Passion Level toggle (slid from My Artists tab)
- **AND** the system SHALL display a coach mark tooltip: "好きなレベルを設定してみよう！"

#### Scenario: Step 5 - Passion Level changed

- **WHEN** a user is at Step 5
- **AND** the user changes the Passion Level of any artist
- **THEN** the system SHALL apply the change as a visual demo only (no server persistence)
- **AND** the system SHALL display a pulse animation on the artist card (300ms)
- **AND** the system SHALL deactivate the spotlight (`deactivateSpotlight()`)
- **AND** the system SHALL advance `onboardingStep` to 7 (COMPLETED)
- **AND** the system SHALL navigate to the landing page

#### Scenario: Step 5 to Step 6 - Spotlight deactivation

- **WHEN** `onboardingStep` advances to 6 (SignUp)
- **THEN** the continuous spotlight SHALL fade out and deactivate (`hidePopover()`)
- **AND** the current target's `anchor-name` SHALL be removed
- **AND** the scroll lock on `<au-viewport>` SHALL be released

#### Scenario: Step 6 - SignUp modal display

- **WHEN** a user is at Step 6
- **THEN** the system SHALL display the Passkey authentication modal
- **AND** the modal SHALL NOT be dismissible (no close button, no backdrop tap, no escape key)
- **AND** the modal message SHALL read: "All set! Create an account to save your preferences and never miss a live show."
- **AND** no spotlight, click-blockers, or orphaned anchor-names SHALL be present in the DOM

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

## Test Cases

### Unit Tests (Vitest — discover-page.spec.ts)

#### TC-TUT-01: Coach mark tap at Step 1 advances to DASHBOARD and navigates

- **Given** `onboardingStep = 1`, `showDashboardCoachMark = true`
- **When** the coach mark `onTap` callback is invoked
- **Then** `onboardingService.setStep(DASHBOARD)` SHALL be called
- **And** `router.load('/dashboard')` SHALL be called

#### TC-TUT-02: showDashboardCoachMark is false with fewer than 3 follows

- **Given** `onboardingStep = 1`, fewer than 3 artists followed
- **Then** `showDashboardCoachMark` SHALL be `false`
- **And** `activateSpotlight()` SHALL NOT be called

### Unit Tests (Vitest — my-artists-page.spec.ts)

#### TC-TUT-03: Step 5 activates spotlight on hype button after artists load

- **Given** `onboardingStep = 5`, artists list has at least 1 artist
- **When** the page loads
- **Then** `onboardingService.activateSpotlight('[data-hype-button]', ...)` SHALL be called

#### TC-TUT-04: Step 5 deactivates spotlight before showing hype explanation

- **Given** `onboardingStep = 5`, spotlight is active
- **When** user selects a passion level
- **Then** `onboardingService.deactivateSpotlight()` SHALL be called before the explanation dialog opens

### Unit Tests (Vitest — discover-page.spec.ts) — Bug Fix Coverage

#### TC-TUT-05: Coach mark tap deactivates spotlight before navigating

- **Given** `onboardingStep = 1`, coach mark is active
- **When** `onCoachMarkTap()` is called
- **Then** `onboardingService.deactivateSpotlight()` SHALL be called before `router.load('/dashboard')`
- **And** `onboardingService.setStep(DASHBOARD)` SHALL be called

### Unit Tests (Vitest — auth-hook.spec.ts) — Bug Fix Coverage

#### TC-TUT-06: Direct nav tap advances step when spotlight is active

- **Given** `onboardingStep = 1`, spotlight is active on Dashboard icon
- **When** the user taps the Dashboard icon in the bottom nav bar (bypassing the coach mark overlay)
- **Then** the auth hook SHALL allow navigation (`canLoad` returns `true`)
- **And** `onboardingService.deactivateSpotlight()` SHALL be called
- **And** `onboardingService.setStep(DASHBOARD)` SHALL be called
- **And** NO "Login required" toast SHALL be published

#### TC-TUT-07: Nav tap blocked when spotlight is NOT active

- **Given** `onboardingStep = 1`, spotlight is NOT active
- **When** the user taps the Dashboard icon (tutorialStep = 3)
- **Then** the auth hook SHALL redirect to the current step's route
- **And** navigation to Dashboard SHALL be denied

### Unit Tests (Vitest — dashboard.spec.ts) — Bug Fix Coverage

#### TC-TUT-08: celebrationShown persists across page reloads

- **Given** `onboardingStep = 3`, Dashboard has been loaded once (celebration shown)
- **When** the page is reloaded (new Dashboard instance)
- **Then** `showCelebration` SHALL be `false` (read from localStorage)
- **And** the Dashboard SHALL be interactive without the celebration overlay blocking interaction

#### TC-TUT-09: Dashboard loads without error when celebrationShown is set

- **Given** `localStorage` has `onboarding.celebrationShown = '1'`
- **When** Dashboard `loading()` is called at Step 3
- **Then** `showCelebration` SHALL be `false`
- **And** the celebration overlay SHALL NOT render

### E2E Tests (Playwright — manual verification)

#### TC-TUT-E2E-01: Full step progression (Step 0 → Step 6)

- Step 0: Tap [Get Started] → navigate to Discover
- Step 1: Follow 3+ artists → coach mark appears on Home icon → tap → navigate to Dashboard
- Step 3: Lane intro sequence → concert card coach mark → tap card → detail sheet
- Step 4: My Artists tab coach mark → tap → navigate to My Artists
- Step 5: Passion Level coach mark → set level → explanation popup
- Step 6: Sign-up modal appears, non-dismissible

#### TC-TUT-E2E-02: No "Login required" toast during onboarding nav

- During onboarding, tap Tickets or Settings nav → verify silent redirect, no toast displayed

#### TC-TUT-E2E-03: Page reload at Step 3 does not replay celebration

- Navigate through onboarding to Step 3 → celebration plays once → reload page → Dashboard loads without celebration, user can interact normally

#### TC-TUT-E2E-04: Coach mark tooltip has no background color

- At any step with a coach mark → verify the tooltip has a transparent background with only white text and drop-shadow, no colored background box

#### TC-TUT-E2E-05: Spotlight visible on all coach mark steps

- At Step 1 (Dashboard icon), Step 3 (concert card), Step 4 (My Artists tab), Step 5 (hype button) → verify the dark overlay with spotlight cutout is visible around the target element
