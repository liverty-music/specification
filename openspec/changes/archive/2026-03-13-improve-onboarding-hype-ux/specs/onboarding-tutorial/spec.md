## MODIFIED Requirements

### Requirement: Linear Step Progression

The system SHALL enforce a strict linear progression through tutorial steps. Users SHALL NOT be able to skip steps or navigate freely during the tutorial. Step 5 is the final interactive step; Step 6 (forced signup modal) is removed.

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

## REMOVED Requirements

### Requirement: Step 5 Passion Level Explanation Timing

**Reason**: Replaced by the notification dialog triggered on unauthenticated slider tap. The previous flow (change passion level → 800ms delay → explanation dialog → advance to Step 6) is removed. Onboarding now completes at Step 5 coachmark dismissal.
**Migration**: Remove the passion explanation dialog component. Remove the 800ms delay timer. Step 5 → Step 6 transition is removed; Step 5 coachmark dismissal advances directly to Step 7 (COMPLETED).

### Requirement: Step 6 - SignUp modal display

**Reason**: The non-dismissible signup modal is replaced by the optional notification dialog (triggered by slider tap) and persistent inline signup banners. Users are no longer forced to sign up to complete onboarding.
**Migration**: Remove the Step 6 signup modal component. Remove the non-dismissible dialog logic. Signup prompts are handled by the notification dialog and `signup-prompt-banner` component. The `OnboardingStep` enum value 6 SHALL be retained for backward compatibility — if a user has `onboardingStep=6` in localStorage from a prior session, the route guard SHALL advance them to Step 7 (COMPLETED).

### Requirement: Step 6 - Passkey authentication success

**Reason**: Authentication success handling moves from Step 6 modal to the notification dialog's [アカウント作成] flow. Guest data merge is triggered from the notification dialog instead.
**Migration**: Move guest data merge trigger to the notification dialog's authentication success callback. The merge logic itself is unchanged.

### Requirement: Step 6 - Page reload

**Reason**: Step 6 no longer exists as a distinct step.
**Migration**: If `onboardingStep=6` is found in localStorage on page load, advance to Step 7 (COMPLETED).

### Requirement: Sign-up Modal Entrance Animation

**Reason**: The sign-up modal (Step 6) is removed entirely.
**Migration**: Remove sign-up modal entrance animation CSS. The notification dialog uses standard dialog entrance animation.
