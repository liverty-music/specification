## REMOVED Requirements

### Requirement: Step 2 - Loading sequence (deprecated for onboarding)

**Reason**: The loading-sequence route is deleted entirely. The Discover page handles concert data fetching inline via fire-and-forget `SearchNewConcerts` calls and a concert data gate. There is no loading screen to redirect to or from.
**Migration**: Remove the Step 2 scenario from the spec. The `OnboardingStep.LOADING` enum value (2) is retained for localStorage backward compatibility — the route mapping is updated to point to `dashboard` so users with `onboardingStep=2` land on Dashboard via the existing step resolution logic.

## MODIFIED Requirements

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
- **AND** when the user taps the Dashboard icon, the system SHALL advance `onboardingStep` to 3 (DASHBOARD)
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
