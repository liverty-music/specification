## ADDED Requirements

### Requirement: Push offer comes before the browser permission prompt

The notification prompt SHALL be the app's own offer to turn on push notifications for new concerts, shown before the browser's permission prompt. The app SHALL show the browser's notification permission prompt only at once after the fan presses the action of a push offer, or turns on the push toggle in Settings; it SHALL never show it on app launch, on a screen load, or on any other event.

#### Scenario: Pressing the offer action shows the browser prompt

- **WHEN** a fan presses the action of a push offer
- **THEN** the browser's notification permission prompt appears at once

#### Scenario: No browser prompt on launch

- **WHEN** a signed-in fan with an undecided notification permission opens the app
- **THEN** no browser permission prompt and no push offer appear on launch

### Requirement: Where the push offer appears

The push offer SHALL appear in exactly two places: the first step of the post-signup sheet (stated by the post-signup dialog surface) and a snack after a saved hype change on My Artists (stated by the My Artists screen). No other screen or surface SHALL show a push offer; the push toggle in Settings stays available at all times.

#### Scenario: Offer after sign-up

- **WHEN** a fan completes sign-up and closes the celebration
- **THEN** the post-signup sheet's first step offers push notifications

#### Scenario: Offer after a hype change

- **WHEN** an eligible signed-in fan saves a hype change on My Artists
- **THEN** a snack offers push notifications

#### Scenario: No offer on other screens

- **WHEN** an eligible fan uses Discovery, the Dashboard, Tickets or an Event page
- **THEN** no push offer appears

### Requirement: Push offer eligibility

The push offer SHALL be shown only to a signed-in fan whose browser notification permission is undecided and whose browser can receive push notifications. On iOS and iPadOS, the browser can receive push notifications only when the app was added to the home screen and opened from there. A guest SHALL never see a push offer. A fan whose browser blocked notifications SHALL never see a push offer; Settings tells them how to change it.

#### Scenario: Guest

- **WHEN** a guest saves a hype change on My Artists
- **THEN** no push offer appears

#### Scenario: Permission already granted

- **WHEN** a signed-in fan whose browser already allows notifications saves a hype change
- **THEN** no push offer appears

#### Scenario: Permission blocked

- **WHEN** a signed-in fan whose browser blocked notifications saves a hype change
- **THEN** no push offer appears

#### Scenario: iOS Safari without the app on the home screen

- **WHEN** a signed-in fan uses the app in iOS Safari without adding it to the home screen and saves a hype change
- **THEN** no push offer appears

### Requirement: Push offer limits

The hype-change push offer SHALL appear at most once per session, a session being one launch of the app. When the fan has let the hype-change offer go unanswered (the snack closed without the action) or declined the browser prompt 3 times in total, the hype-change offer SHALL stop for good on that browser. The post-signup sheet shows its offer once per sign-up, independently of these limits.

#### Scenario: Once per session

- **WHEN** the fan saw the hype-change offer in this session and saves another hype change
- **THEN** no push offer appears

#### Scenario: Next session

- **WHEN** the fan let the offer go unanswered once, relaunches the app and saves a hype change
- **THEN** the offer appears again

#### Scenario: Third unanswered offer stops it

- **WHEN** the fan has let the offer go unanswered or declined the browser prompt 3 times
- **AND** relaunches the app and saves a hype change
- **THEN** no push offer appears

### Requirement: Outcome of the browser permission prompt

After the fan answers the browser's permission prompt opened from a push offer, the app SHALL report the outcome. When the fan allows notifications, the app SHALL register push notifications for this browser and show a snack 「新しいライブを通知します。設定からいつでも止められます」 (EN "We'll notify you of new concerts. You can turn this off in Settings anytime."). When the fan blocks notifications, the app SHALL show a snack 「通知はブロックされています。ブラウザの設定から変更できます」 (EN "Notifications are blocked. You can change this in your browser settings."). When the fan closes the prompt without answering, the app SHALL show nothing and SHALL count it as one unanswered offer.

#### Scenario: Fan allows

- **WHEN** the fan allows notifications in the browser prompt
- **THEN** new concerts that match the fan's hype levels reach this browser by push
- **AND** a snack says 「新しいライブを通知します。設定からいつでも止められます」

#### Scenario: Fan blocks

- **WHEN** the fan blocks notifications in the browser prompt
- **THEN** a snack says 「通知はブロックされています。ブラウザの設定から変更できます」
- **AND** no push offer appears again

#### Scenario: Fan closes the prompt

- **WHEN** the fan closes the browser prompt without answering
- **THEN** no snack appears and the offer counts as unanswered once

## REMOVED Requirements

### Requirement: Notification Prompt Placement

**Reason**: The app-wide notification toast is removed. The push offer appears only after sign-up and after a hype change, when the fan's intent is clear.
**Migration**: See "Where the push offer appears".

### Requirement: Notification Prompt Blocked When Not Authenticated

**Reason**: Restated with the other eligibility rules.
**Migration**: See "Push offer eligibility".

### Requirement: Notification Prompt Blocked During Onboarding

**Reason**: Referred to a step machine that no longer exists. A guest is never offered push, and a fan who signs up leaves onboarding.
**Migration**: See "Push offer eligibility".

### Requirement: Single Prompt Per Session

**Reason**: The push offer no longer competes with a PWA install prompt; the post-signup sheet asks for each in its own step, and the hype-change offer has its own per-session limit.
**Migration**: See "Push offer limits" and the post-signup dialog surface.

### Requirement: Notification Prompt Priority Over Disruptive PWA Prompts

**Reason**: The app-wide toast it ranked is removed.
**Migration**: None.

### Requirement: Notification Prompt Eligible on First Post-Completion Session

**Reason**: The second-session toast is removed; the offer is tied to sign-up and to hype changes instead of to the session count.
**Migration**: See "Where the push offer appears". The stored session counters lose their reader.

### Requirement: Dismissed notification prompt does not reappear

**Reason**: Replaced by the 3-times limit of the hype-change offer and by the rule that a browser block ends all offers.
**Migration**: See "Push offer limits" and "Push offer eligibility". The stored dismissal flag of the removed toast is no longer read.
