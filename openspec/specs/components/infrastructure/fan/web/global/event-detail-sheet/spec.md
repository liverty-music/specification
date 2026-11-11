# Event Detail Sheet

## Purpose

Shows a detail sheet for a selected concert with a hero image, venue and time information, and an accessible ticket-journey status control that lets a user track their ticket-acquisition progress independent of actual ticket sales.

## Requirements

### Requirement: Event Detail Sheet Hero Image
The event detail sheet SHALL display the artist's background image as a hero section above the existing artist header when `artist_background` is available. The hero image SHALL NOT be displayed when no background image exists, preserving the current layout.

#### Scenario: Artist has background image
- **WHEN** the detail sheet opens for an event whose artist has `artist_background` in their fanart data
- **THEN** the sheet SHALL display the background image in a hero section above the artist header with `aspect-ratio: 16/9` and `object-fit: cover`

#### Scenario: Artist has no background image
- **WHEN** the detail sheet opens for an event whose artist has no `artist_background`
- **THEN** the sheet SHALL render the existing layout without a hero section

#### Scenario: Hero image with gradient fade
- **WHEN** the hero image is displayed
- **THEN** the bottom edge of the hero section SHALL fade into the sheet background color via a gradient overlay to ensure visual continuity

### Requirement: Event detail sheet computes URLs and handles touch dismiss
The event detail sheet SHALL compute Google Maps and Calendar URLs and support touch drag-to-dismiss with a 100px threshold.

#### Scenario: Google Maps URL construction
- **WHEN** the sheet is opened with an event that has a venue name
- **THEN** `googleMapsUrl` SHALL return a valid Google Maps search URL for the venue

#### Scenario: Google Calendar URL construction
- **WHEN** the sheet is opened with an event
- **THEN** `calendarUrl` SHALL return a Google Calendar URL with correct start and end times

#### Scenario: Touch drag exceeding threshold closes sheet
- **WHEN** a touch drag moves more than 100px downward
- **THEN** the sheet SHALL close

#### Scenario: Touch drag below threshold keeps sheet open
- **WHEN** a touch drag moves less than 100px
- **THEN** the sheet SHALL remain open

### Requirement: Ticket Status selection contrast

The currently selected status SHALL be conveyed primarily through a solid fill versus outlined unselected states, rather than through background color intensity or opacity. The selected node SHALL remain clearly distinguishable from unselected nodes for every status value, including `LOST`.

#### Scenario: Selected LOST is clearly distinguishable

- **WHEN** the current status is `LOST`
- **THEN** the `LOST` node SHALL be solid-filled
- **AND** it SHALL be visually distinct from the unselected/outlined nodes

### Requirement: Ticket Status semantic color and non-color cues

Each status SHALL carry a meaning-based color and a non-color cue (icon plus text label) so the control is understandable without relying on color alone. `UNPAID` SHALL be the highest-attention color (amber/orange) to signal a required payment action, `PAID` SHALL use a success color (green), `LOST` SHALL use a failure color (red), and `TRACKING`/`APPLIED` SHALL use neutral/in-progress colors.

#### Scenario: UNPAID is emphasized as action-required

- **WHEN** the current status is `UNPAID`
- **THEN** the `UNPAID` node SHALL use the highest-attention (amber/orange) color
- **AND** it SHALL include a non-color action cue

#### Scenario: Meaning survives without color

- **WHEN** any status node is rendered
- **THEN** it SHALL include a text label and a non-color cue (icon) in addition to color

### Requirement: Ticket Journey UI is independent of ticket sales
The Ticket Journey status UI (concert-card badge and detail-sheet status control) SHALL be available to authenticated users independently of any ticket purchase, NFT minting, ZK proof generation, or ticket sales navigation features. Hiding or removing those sales-side features SHALL NOT affect the availability of the Ticket Journey UI.

#### Scenario: Journey UI visible when ticket sales nav is hidden

- **WHEN** the Tickets bottom-nav tab is hidden (ticket sales feature not yet service-ready)
- **THEN** the journey status badge SHALL still appear on event cards for users who have a journey status
- **AND** the journey selection control SHALL still appear in the event detail sheet for authenticated users

#### Scenario: Journey UI does not depend on ticket purchase flow

- **WHEN** a user has not completed any ticket purchase or NFT minting
- **THEN** the user SHALL still be able to set and view their journey status (e.g. `tracking`, `applied`, `lost`, `unpaid`, `paid`) via the UI

### Requirement: Ticket Status saving failures and double taps

When saving or removing a journey status fails, the sheet SHALL keep showing the status the fan had before and SHALL show no error message. While a change is being saved, further status selections in the sheet SHALL be ignored.

#### Scenario: Saving fails

- **WHEN** a signed-in fan picks Paid for an event whose status is Unpaid and saving fails
- **THEN** the sheet still shows Unpaid and no error message appears

#### Scenario: Second tap while saving

- **WHEN** the fan picks Applied and, before it is saved, picks Lost
- **THEN** the second pick is ignored and the sheet shows Applied once the first change is saved

### Requirement: Leaving for the source and adding to a calendar are reported

When the fan opens the concert's source link or its add-to-calendar link from the event detail sheet, the fan app SHALL send one usage analytics event naming which link, with the event and the artist.

#### Scenario: Source link
- **WHEN** the fan taps the source link of a concert in the detail sheet
- **THEN** one event is sent naming the source link, the event and the artist

### Requirement: Adding to the calendar starts tracking

When a signed-in fan with no journey for the event chooses add to calendar in the event detail sheet, the app SHALL start tracking the event as an inference (TicketJourneyService.InferTracking) at once, and every screen SHALL show Tracking for the event once it is saved. When the fan comes back to the app after the calendar opened, or at once when the app stayed in view, the sheet SHALL show a snack that reads 「🔔 チケット販売の通知を受け取ります」 (EN "🔔 You will get ticket sale notifications."), with the action 「取り消す」 (EN "Undo"). The snack SHALL stay 10 seconds unless the fan presses the action. Pressing it SHALL remove the journey, and no screen SHALL then show a status for the event. A guest's calendar add, a fan who already has a journey for the event, and a save that fails SHALL start nothing and show no snack.

#### Scenario: Calendar add from the sheet

- **WHEN** a signed-in fan with no journey for an event chooses add to calendar, the calendar opens, and the fan comes back to the app
- **THEN** the sheet shows 「🔔 チケット販売の通知を受け取り中 ✓」, the Dashboard shows the 🔔 badge for the event, and the snack 「🔔 チケット販売の通知を受け取ります」 offers 「取り消す」

#### Scenario: Undo

- **WHEN** the fan presses 「取り消す」 on that snack
- **THEN** neither the sheet nor the Dashboard shows a status for the event

#### Scenario: Fan already has a journey

- **WHEN** a signed-in fan whose journey for the event is Applied chooses add to calendar
- **THEN** the journey stays Applied and no snack appears

#### Scenario: Guest

- **WHEN** a guest chooses add to calendar
- **THEN** the calendar opens, no journey is requested from the server and no snack appears

### Requirement: A hype level raised by a journey change is shown with undo

When a signed-in fan's Applied, Unpaid or Paid in the event detail sheet is saved and the app raised the fan's hype level for the concert's artist as a result, the sheet SHALL show a snack that says the new level in the place words and forms of the My Artists hype snack (「{{name}}の{{places}}の新着ライブをプッシュ通知します🔔」, or 「…をプッシュ通知で受け取ろう🔔」 when push is off for this browser), with the action 「取り消す」 (EN "Undo") in place of the push offer, and the Dashboard SHALL highlight the artist's concerts the new level matches. The snack SHALL stay 10 seconds unless the fan presses the action. Pressing it SHALL set the previous level as the fan's own choice; when that save fails, the raised level stays shown and a message says the change failed. When the level was not raised, no snack SHALL appear.

#### Scenario: Applied for a distant concert raises the level

- **WHEN** a signed-in fan whose browser receives push and whose hype for ヨルシカ is Nearby set by default saves Applied for ヨルシカ's concert in the away lane
- **THEN** the snack reads 「ヨルシカの全ての新着ライブをプッシュ通知します🔔」 with 「取り消す」 and the concert's card on the Dashboard is highlighted

#### Scenario: Undo the raise

- **WHEN** the fan presses 「取り消す」 on that snack
- **THEN** ヨルシカ is at Nearby, set by the fan, and the away-lane card is no longer highlighted

#### Scenario: Level not raised

- **WHEN** the fan's hype for the artist was set by the fan and the fan saves Applied
- **THEN** no snack appears

### Requirement: Status controls are shown to signed-in fans only

The row of the other four statuses SHALL be rendered only when the user is authenticated, and only an authenticated user's press of the ticket sale notification button SHALL change a status. An unauthenticated (guest) user SHALL see the ticket sale notification button, which starts sign-up as "A guest's notification button starts sign-up" states, and the official site button, and no status row.

#### Scenario: Authenticated user sees the status controls

- **WHEN** an authenticated user opens the concert detail sheet
- **THEN** the ticket sale notification button and the row of 申込済み, 当選・未入金, 入金済み and 落選 SHALL be visible
- **AND** the user SHALL be able to select any of the five statuses with one tap, except Tracking while the status is Paid

#### Scenario: Unauthenticated user sees no status row

- **WHEN** an unauthenticated (guest) user opens the concert detail sheet
- **THEN** the row of the four statuses SHALL NOT be rendered
- **AND** no RPC call to `TicketJourneyService/SetStatus` SHALL be made

### Requirement: Ticket Status buttons accessibility

The ticket sale notification button and each status in the row SHALL be a button exposing whether it is selected (`aria-pressed`), with at most one of the five selected. Each status in the row SHALL have an accessible name made of its canonical label, and the notification button an accessible name made of its visible text; each SHALL have a tap target of at least 48px.

#### Scenario: Pressed state

- **WHEN** the fan's status for the event is Applied
- **THEN** the 申込済み button exposes `aria-pressed="true"`
- **AND** the four other buttons expose `aria-pressed="false"`

#### Scenario: Keyboard

- **WHEN** a keyboard user moves focus through the ticket section
- **THEN** each button the section shows (five, or four with Paid) is reached with Tab and activated with Enter or Space

### Requirement: The ticket section follows the venue and holds the official site button

The event detail sheet SHALL show, in this order: the hero image when there is one, the artist and the event title, the date and times with the add-to-calendar link, the venue with its map link, the out-of-range notice when it applies, and the ticket section. The ticket section SHALL hold, in this order, the ticket sale notification button, the row of the other four statuses for a signed-in fan, the push line when the status has one, and the button that opens the concert's official page (「公式サイトでチケットを見る」, EN "See tickets on the official site"). The sheet SHALL show no other button that opens the official page.

#### Scenario: Order of the sheet

- **WHEN** a signed-in fan opens the detail sheet of a concert with a hero image
- **THEN** the sheet shows the hero image, the artist, the date with 「カレンダーに追加」, the venue with its map link, and then the ticket section ending with 「公式サイトでチケットを見る」

#### Scenario: Back from the official site

- **WHEN** the fan opens 「公式サイトでチケットを見る」, enters a lottery there and comes back to the app
- **THEN** the sheet still shows the ticket section, with 申込済み in the row above the official site button

### Requirement: The ticket section leads with the ticket sale notification button

The ticket section SHALL start with one full-width button for the Tracking status. With no status, or any status other than Tracking, it SHALL read 「🔔 チケット販売の通知を受け取る」 (EN "🔔 Get ticket sale notifications"), shown as the section's primary button when the fan has no status or the status is 落選 (Lost), and as a secondary button otherwise; with Lost it SHALL read 「🔔 次のチケット販売の通知を受け取る」 (EN "🔔 Get notified of the next ticket sale"). With Tracking it SHALL read 「🔔 チケット販売の通知を受け取り中 ✓」 (EN "🔔 Getting ticket sale notifications ✓") in the selected style. With Paid the button SHALL NOT be shown.

Under the button, a signed-in fan SHALL see one row with the other four statuses as buttons, each with its canonical icon and label: 📝 申込済み › 💰 当選・未入金 › 🎟️ 入金済み, and 💔 落選 set apart from them; the row wraps on a narrow screen. Pressing an unselected button SHALL set that status; pressing the selected button, including the notification button while it reads 「…受け取り中 ✓」, SHALL remove the fan's status for the event. Every status, and no status, SHALL be reachable with one tap from any status, except Tracking from Paid: with Paid the notification button is hidden, so the fan first clears Paid by pressing 入金済み.

#### Scenario: Start tracking

- **WHEN** a signed-in fan with no status for an event presses 「🔔 チケット販売の通知を受け取る」
- **THEN** the status is Tracking and the button reads 「🔔 チケット販売の通知を受け取り中 ✓」

#### Scenario: Stop tracking

- **WHEN** a fan whose status is Tracking presses 「🔔 チケット販売の通知を受け取り中 ✓」
- **THEN** the fan has no status for the event

#### Scenario: Applied in one tap

- **WHEN** a fan whose status is Tracking presses 📝 申込済み
- **THEN** the status is Applied, 申込済み is selected, and the notification button reads 「🔔 チケット販売の通知を受け取る」 as a secondary button

#### Scenario: Clear a status

- **WHEN** a fan whose status is Applied presses the selected 📝 申込済み
- **THEN** the fan has no status for the event

#### Scenario: After losing

- **WHEN** a fan's status is 落選
- **THEN** the primary button reads 「🔔 次のチケット販売の通知を受け取る」 and pressing it sets Tracking

#### Scenario: Ticket secured

- **WHEN** a fan's status is 入金済み
- **THEN** the notification button is not shown and 🎟️ 入金済み is selected

### Requirement: The push line says what the current status brings

Under the status controls the ticket section SHALL show one line for the statuses below, and none for the others (Unpaid shows its own line, Paid and Lost show none):

| status | push is on for this browser | push is off for this browser |
|---|---|---|
| none | 販売開始と抽選の締め切りをプッシュ通知で受け取れます | 販売開始と抽選の締め切りをプッシュ通知で受け取れます |
| Tracking | 販売開始と抽選の締め切りをプッシュ通知します🔔 | 販売開始と抽選の締め切りをプッシュ通知で受け取ろう🔔, with the push offer |
| Applied | 発表日がわかる抽選は、結果発表の日にプッシュ通知します🔔 | 発表日がわかる抽選は、結果発表の日のプッシュ通知を受け取ろう🔔, with the push offer |
| Unpaid | 期限までに入金を済ませましょう | 期限までに入金を済ませましょう |

The English locale SHALL show equivalent texts. Where the fan is not eligible for the push offer, the line carries 「設定」 instead, as the notification prompt surface states.

#### Scenario: Tracking with push on

- **WHEN** a fan whose browser receives push has Tracking for the event
- **THEN** the line reads 「販売開始と抽選の締め切りをプッシュ通知します🔔」

#### Scenario: Tracking with push off

- **WHEN** a fan whose notification permission is undecided has Tracking for the event
- **THEN** the line reads 「販売開始と抽選の締め切りをプッシュ通知で受け取ろう🔔」 with the push offer

#### Scenario: Applied

- **WHEN** a fan whose browser receives push has Applied for the event
- **THEN** the line reads 「発表日がわかる抽選は、結果発表の日にプッシュ通知します🔔」

### Requirement: A guest's notification button starts sign-up

A guest SHALL see the ticket section with 「🔔 チケット販売の通知を受け取る」 as its primary button, the line 「アカウントを作ると、販売開始をプッシュ通知で受け取れます」 (EN "Create an account to get ticket sale notifications."), and the official site button. Pressing the notification button SHALL start sign-up. After the account is resolved, the app SHALL return to the same concert's detail sheet and set Tracking for the event as the fan's own choice; when that save fails, the sheet shows the button unpressed and no error message.

#### Scenario: Guest presses the button

- **WHEN** a guest presses 「🔔 チケット販売の通知を受け取る」 on a concert's detail sheet
- **THEN** sign-up starts

#### Scenario: Back after sign-up

- **WHEN** that guest completes sign-up
- **THEN** the same concert's detail sheet is open and reads 「🔔 チケット販売の通知を受け取り中 ✓」

### Requirement: The out-of-range notice widens what is pushed

When the fan follows the concert's artist and the fan's hype level for the artist does not match the concert, the sheet SHALL show a notice under the venue. It SHALL say what the current level pushes, with the place words of the My Artists hype snack set in a larger, highlighted style, and offer one button that sets the artist's hype level to the lowest level that matches the concert, as the fan's own choice:

| current level | notice | button, by the concert's lane |
|---|---|---|
| Home | 今は**東京**の新着ライブだけプッシュ通知対象です | near: 東京周辺の新着ライブも受け取る; away: 全ての新着ライブを受け取る |
| Nearby | 今は**東京周辺**の新着ライブだけプッシュ通知対象です | away: 全ての新着ライブを受け取る |
| Watch | 今は新着ライブをプッシュ通知していません | home: 東京の新着ライブを受け取る; near: 東京周辺の新着ライブを受け取る; away: 全ての新着ライブを受け取る |

After the level is saved, the notice SHALL read 「**{{places}}**の新着ライブをプッシュ通知します🔔」 for the new level, or 「…をプッシュ通知で受け取ろう🔔」 with the push offer when push is off for this browser (with 「登録する」 for a guest), and no snack SHALL appear. When the save fails, the notice SHALL stay as it was and a message SHALL say the change failed. A concert the level matches, and a concert of an artist the fan does not follow, SHALL show no notice.

#### Scenario: Nearby fan opens a distant concert

- **WHEN** a fan with home JP-13 and ヨルシカ at Nearby opens ヨルシカ's concert in Fukuoka
- **THEN** the notice reads 「今は**東京周辺**の新着ライブだけプッシュ通知対象です」 with 「全ての新着ライブを受け取る」

#### Scenario: Widening

- **WHEN** the fan presses 「全ての新着ライブを受け取る」 and the browser receives push
- **THEN** ヨルシカ is at Away, set by the fan, the notice reads 「**全て**の新着ライブをプッシュ通知します🔔」, and the concert's card is highlighted

#### Scenario: Matched concert

- **WHEN** a fan with ヨルシカ at Away opens any ヨルシカ concert
- **THEN** no notice is shown

#### Scenario: Artist not followed

- **WHEN** a fan opens, from the All Nearby view, a concert of an artist the fan does not follow
- **THEN** no notice is shown
