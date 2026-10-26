# Notification Prompt

## Purpose

Prompts a signed-in user, once onboarding is complete, to grant push-notification permission, limiting itself to one prompt per session, taking priority over other disruptive prompts, and never reappearing once dismissed.

## Requirements

### Requirement: The permission answer is reported

After the fan answers the browser's push-permission request, the fan app SHALL send one usage analytics event with the answer (granted, denied, or dismissed without an answer) and where the request started: the push offer after a hype change (the notification prompt), the post-signup sheet, Settings, or checkout.

#### Scenario: Fan denies
- **WHEN** the fan presses 「オンにする」 on the push offer and then blocks notifications in the browser's request
- **THEN** one event is sent with the answer denied and the notification prompt as its start

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
