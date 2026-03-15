# Onboarding Tutorial

## Purpose

Defines the linear onboarding tutorial flow that guides new users through artist discovery, dashboard interaction, and account creation.
## Requirements
### Requirement: Onboarding Step State Management

The system SHALL maintain an `onboardingStep` numeric value in LocalStorage under the key `liverty:onboardingStep` to track the user's progress through the linear tutorial. Valid values are 0-5 (in-progress), 6 (legacy: immediately migrated to 7), and 7 (COMPLETED).

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

The system SHALL enforce a strict linear progression through tutorial steps. Users SHALL NOT be able to skip steps or navigate freely during the tutorial. Step 5 is the final interactive step; Step 6 (forced signup modal) is removed.

#### Scenario: Step 0 - Landing Page entry

- **WHEN** a user is at Step 0 (LP)
- **AND** the user taps the [Get Started] CTA
- **THEN** the system SHALL advance `onboardingStep` to 1
- **AND** navigate to the Artist Discovery screen

#### Scenario: Step 1 - Artist Discovery completion with concert data gate

- **WHEN** a user is at Step 1 (Artist Discovery / Bubble UI)
- **AND** the user has followed 3 or more artists via bubble taps
- **AND** concert search results have been received for all followed artists (or timed out after 15 seconds per artist)
- **AND** `ConcertService/List` returns at least 1 date group for the followed artists
- **THEN** the system SHALL activate a coach mark spotlight on the Dashboard icon in the bottom navigation bar (target: `[data-nav-dashboard]`)
- **AND** the coach mark SHALL display the message: "タイムテーブルを見てみよう！"
- **AND** when the user taps the Dashboard icon, the system SHALL advance `onboardingStep` to 3 (DASHBOARD), skipping Step 2 (LOADING)
- **AND** the system SHALL navigate to the Dashboard (`/dashboard`)

#### Scenario: Step 1 - Concert searches complete with no results

- **WHEN** a user is at Step 1 (Artist Discovery / Bubble UI)
- **AND** the user has followed 3 or more artists
- **AND** concert search results have been received for all followed artists (or timed out)
- **AND** `ConcertService/List` returns 0 date groups
- **THEN** the system SHALL NOT activate the Dashboard coach mark
- **AND** the system SHALL update the guidance HUD message to: "No upcoming events found yet — try following more artists!"
- **AND** the system SHALL re-evaluate the concert data gate each time a new artist is followed and their concert search completes

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

#### Scenario: Step 3 - Dashboard with no concert data (fallback)

- **WHEN** a user is at Step 3 (Dashboard)
- **AND** `ConcertService/List` returns 0 date groups (e.g., user reached Dashboard via direct nav tap bypassing the concert data gate)
- **THEN** the system SHALL skip the lane introduction sequence entirely
- **AND** the system SHALL advance `onboardingStep` to 4 (DETAIL)
- **AND** the system SHALL activate the spotlight on the [My Artists] tab in the bottom navigation bar
- **AND** the system SHALL display a coach mark tooltip: "アーティスト一覧も見てみよう！"

#### Scenario: Step 3 - Concert card tap

- **WHEN** a user is at Step 3
- **AND** the user taps the spotlighted concert card
- **THEN** the system SHALL advance `onboardingStep` to 4
- **AND** open the concert detail sheet (popover)

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

#### Scenario: Step 5 - Hype Header Coachmark

- **WHEN** a user is at Step 5 (My Artists)
- **THEN** the system SHALL display the sticky hype header legend with `[data-hype-header]` attribute
- **AND** the system SHALL spotlight the sticky header using the coach mark overlay
- **AND** the coach mark message SHALL read: "絶対に見逃したくないアーティストの熱量を上げておこう"

#### Scenario: Step 5 - Coachmark dismissal completes onboarding

- **WHEN** a user is at Step 5
- **AND** the user taps the coach mark overlay to dismiss it
- **THEN** the system SHALL advance `onboardingStep` to 7 (COMPLETED)
- **AND** the system SHALL remove all tutorial UI restrictions (coach marks, spotlight, interaction locks)
- **AND** the user SHALL have full unrestricted access to the My Artists page

#### Scenario: Step 5 - Unauthenticated slider tap triggers notification dialog

- **WHEN** a user is at Step 5 or has completed onboarding (Step >= 7)
- **AND** the user is unauthenticated
- **AND** the user taps a hype slider dot
- **THEN** the system SHALL display the notification dialog (single page)
- **AND** the dialog SHALL display hype tier → notification scope mapping:
  - 👀 通知なし
  - 🔥 地元のライブを通知
  - 🔥🔥 近くのライブも通知
  - 🔥🔥🔥 全国のライブを通知
- **AND** the dialog SHALL display: "通知を受け取るにはアカウント登録が必要です"
- **AND** the dialog SHALL present two buttons: [アカウント作成] (primary) and [あとで] (ghost)

#### Scenario: Notification dialog - アカウント作成

- **WHEN** the user taps [アカウント作成] in the notification dialog
- **THEN** the system SHALL initiate the Zitadel OIDC Passkey authentication flow
- **AND** upon successful authentication, the system SHALL trigger the guest data merge process
- **AND** after merge, hype sliders SHALL become interactive

#### Scenario: Notification dialog - あとで

- **WHEN** the user taps [あとで] in the notification dialog
- **THEN** the dialog SHALL close
- **AND** the hype slider SHALL remain at the current position (WATCH for all artists)
- **AND** the inline signup banner SHALL become visible on My Artists and Dashboard pages

#### Scenario: Notification dialog shown once per session

- **WHEN** the user has dismissed the notification dialog with "あとで"
- **AND** the user taps another slider dot in the same session
- **THEN** the notification dialog SHALL NOT be shown again
- **AND** the slider SHALL NOT move (still unauthenticated)

#### Scenario: Step 6 - SignUp modal display (REMOVED)

**Reason**: The non-dismissible signup modal is replaced by the optional notification dialog (triggered by slider tap) and persistent inline signup banners. Users are no longer forced to sign up to complete onboarding.
**Migration**: Remove the Step 6 signup modal component. Remove the non-dismissible dialog logic. Signup prompts are handled by the notification dialog and `signup-prompt-banner` component. The `OnboardingStep` enum value 6 SHALL be retained for backward compatibility — if a user has `onboardingStep=6` in localStorage from a prior session, the route guard SHALL advance them to Step 7 (COMPLETED).

#### Scenario: Step 6 - Passkey authentication success (REMOVED)

**Reason**: Authentication success handling moves from Step 6 modal to the notification dialog's [アカウント作成] flow. Guest data merge is triggered from the notification dialog instead.
**Migration**: Move guest data merge trigger to the notification dialog's authentication success callback. The merge logic itself is unchanged.

#### Scenario: Step 6 - Page reload (REMOVED)

**Reason**: Step 6 no longer exists as a distinct step.
**Migration**: If `onboardingStep=6` is found in localStorage on page load, advance to Step 7 (COMPLETED).

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
- **AND** if still not found, the system SHALL fully deactivate the coach mark overlay: close the popover, release scroll lock, clear anchor-name assignments, and log an error
- **AND** no click-blockers, spotlight elements, or scroll locks SHALL remain in the DOM after deactivation

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

### Requirement: No Permission Prompts During Onboarding Steps 1-5

The system SHALL suppress all permission prompts (PWA install banner, push notification opt-in) while the user is progressing through onboarding Steps 1-5. Permission prompts are deferred until after Step 7 (COMPLETED).

#### Scenario: PWA install suppressed during tutorial

- **WHEN** the user is at any onboarding step between 1 and 5
- **AND** the browser fires the `beforeinstallprompt` event
- **THEN** the system SHALL capture the event for later use
- **BUT** the system SHALL NOT display the PWA install banner

#### Scenario: Notification prompt suppressed during tutorial

- **WHEN** the user is at any onboarding step between 1 and 5
- **THEN** the system SHALL NOT render or evaluate the notification prompt component

#### Scenario: Prompts become eligible after completion

- **WHEN** the user completes Step 5 and transitions to Step 7 (COMPLETED)
- **THEN** permission prompts SHALL become eligible according to the prompt-timing capability rules
- **AND** the onboarding tutorial SHALL NOT block prompt display after this point

---

### Requirement: Step 5 Passion Level Explanation Timing (REMOVED)

**Reason**: Replaced by the notification dialog triggered on unauthenticated slider tap. The previous flow (change passion level → 800ms delay → explanation dialog → advance to Step 6) is removed. Onboarding now completes at Step 5 coachmark dismissal.
**Migration**: Remove the passion explanation dialog component. Remove the 800ms delay timer. Step 5 → Step 6 transition is removed; Step 5 coachmark dismissal advances directly to Step 7 (COMPLETED).

---

### Requirement: Sign-up Modal Entrance Animation (REMOVED)

**Reason**: The sign-up modal (Step 6) is removed entirely.
**Migration**: Remove sign-up modal entrance animation CSS. The notification dialog uses standard dialog entrance animation.

