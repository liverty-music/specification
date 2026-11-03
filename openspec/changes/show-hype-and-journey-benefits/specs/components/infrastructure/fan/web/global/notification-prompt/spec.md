## MODIFIED Requirements

### Requirement: The permission answer is reported

After the fan answers the browser's push-permission request, the fan app SHALL send one usage analytics event with the answer (granted, denied, or dismissed without an answer) and where the request started: the hype snack on My Artists (the notification prompt), the event detail sheet, the post-signup sheet, Settings, or checkout.

#### Scenario: Fan denies
- **WHEN** the fan presses 「オンにする」 on the push offer and then blocks notifications in the browser's request
- **THEN** one event is sent with the answer denied and the notification prompt as its start

#### Scenario: Fan allows from the event detail sheet
- **WHEN** the fan presses the push offer next to the push line of the ticket section and allows notifications in the browser's request
- **THEN** one event is sent with the answer granted and the event detail sheet as its start

### Requirement: Where the push offer appears

The push offer SHALL appear only in these places: the first step of the post-signup sheet (stated by the post-signup dialog surface), the hype snack on My Artists (stated by the My Artists screen), and next to the push line of the ticket section and of the out-of-range notice in the event detail sheet (stated by the event detail sheet surface). No other screen or surface SHALL show a push offer; the push toggle in Settings stays available at all times.

#### Scenario: Offer after sign-up

- **WHEN** a fan completes sign-up and closes the celebration
- **THEN** the post-signup sheet's first step offers push notifications

#### Scenario: Offer after a hype change

- **WHEN** an eligible signed-in fan saves a hype change on My Artists
- **THEN** the hype snack offers push notifications

#### Scenario: Offer in the ticket section

- **WHEN** an eligible signed-in fan opens the event detail sheet of an event they track
- **THEN** the push line of the ticket section offers push notifications

#### Scenario: No offer on other screens

- **WHEN** an eligible fan uses Discovery, the Dashboard outside the event detail sheet, Tickets or an Event page
- **THEN** no push offer appears

### Requirement: Push offer eligibility

The push offer SHALL be shown only to a signed-in fan whose browser notification permission is undecided and whose browser can receive push notifications. On iOS and iPadOS, the browser can receive push notifications only when the app was added to the home screen and opened from there. A guest SHALL never see a push offer. Where a signed-in fan whose push is off is not eligible, because the browser blocked notifications or cannot receive them, the place of the offer SHALL show the action 「設定」 instead, which opens Settings, where the fan is told how to turn notifications on.

#### Scenario: Guest

- **WHEN** a guest saves a hype change on My Artists
- **THEN** no push offer appears

#### Scenario: Permission already granted

- **WHEN** a signed-in fan whose browser already allows notifications and is registered for push saves a hype change
- **THEN** no push offer appears

#### Scenario: Permission blocked

- **WHEN** a signed-in fan whose browser blocked notifications saves a hype change
- **THEN** no push offer appears and the hype snack's action is 「設定」

#### Scenario: iOS Safari without the app on the home screen

- **WHEN** a signed-in fan uses the app in iOS Safari without adding it to the home screen and saves a hype change
- **THEN** no push offer appears and the hype snack's action is 「設定」

### Requirement: Outcome of the browser permission prompt

After the fan answers the browser's permission prompt opened from a push offer, the app SHALL report the outcome. When the fan allows notifications, the app SHALL register push notifications for this browser and show a snack 「新しいライブを通知します。設定からいつでも止められます」 (EN "We'll notify you of new concerts. You can turn this off in Settings anytime."). When the fan blocks notifications, the app SHALL show a snack 「通知はブロックされています。ブラウザの設定から変更できます」 (EN "Notifications are blocked. You can change this in your browser settings."). When the fan closes the prompt without answering, the app SHALL show nothing.

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
- **THEN** no snack appears

## REMOVED Requirements

### Requirement: Push offer limits

**Reason**: Replaced by "Only the post-signup offer is limited": the hype snack and the event detail sheet offer push every time push is off, because the fan has just asked for something only push delivers.
**Migration**: None. The device counters of unanswered offers are no longer read; the frontend stops writing them.

## ADDED Requirements

### Requirement: Only the post-signup offer is limited

The post-signup sheet SHALL show its offer once per sign-up. The offers in the hype snack and in the event detail sheet SHALL have no limit of their own: each appears whenever its surface shows it and the fan is eligible, because the fan has just asked for something only push delivers.

#### Scenario: Every hype change with push off

- **WHEN** an eligible fan saw the offer in the hype snack, let it go unanswered, and saves another hype change in the same session
- **THEN** the hype snack offers push notifications again

#### Scenario: After several unanswered offers

- **WHEN** an eligible fan has let the offer go unanswered 5 times and opens the event detail sheet of an event they track
- **THEN** the push line of the ticket section still offers push notifications
