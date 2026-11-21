# Delta for concert-sheet

## ADDED Requirements

### Requirement: The ticket sale notification button's guide moment

When the concert sheet opens for a concert the fan has no status for, or the status 落選 (Lost), and the fan has no journey for any event (a guest never has one), the sheet SHALL show a guide moment on the ticket sale notification button: the button glows and swings like a bell, and the line 「気になるライブは見逃しNG！」 (EN "Don't miss the concerts you care about!") is shown inside the sheet directly above the ticket section. No sound SHALL play. Pressing the button SHALL end the moment and count as using it. The concert sheet on Welcome SHALL show no guide moment.

#### Scenario: First concert a guest opens
- **WHEN** a guest opens a concert's detail sheet from the Timetable for the first time on this device
- **THEN** the 🔔 button glows and 「気になるライブは見逃しNG！」 is shown above the ticket section

#### Scenario: Concert already tracked
- **WHEN** a signed-in fan opens the sheet of a concert whose status is Tracking
- **THEN** no guide moment is shown in the sheet

#### Scenario: Fan who tracks other concerts
- **WHEN** a signed-in fan who has a journey for another event opens a concert with no status on a new device
- **THEN** no guide moment is shown in the sheet

## MODIFIED Requirements

### Requirement: A guest's notification button starts sign-up

A guest SHALL see the ticket section with 「🔔 チケット販売の通知を受け取る」 as its primary button and the official site button, and no push line. Each press of the notification button by a guest SHALL open a dialog over the sheet that says notifications need an account: the heading 「おっと、まだアカウントを持っていないね？」 (EN "Looks like you don't have an account yet?"), the line 「通知に必要なアカウントは無料ですぐに作成できるよ！」 (EN "The account you need for notifications is free and quick to make!"), and two actions, 「あとで」 (EN "Later") and 「Sign Up」. 「Sign Up」 SHALL start sign-up. 「あとで」, the Escape key and a tap on the backdrop SHALL close the dialog and leave the sheet as it was, with no sign-up started. After the account is resolved, the app SHALL return to the same concert's detail sheet and set Tracking for the event as the fan's own choice; when that save fails, the sheet shows the button unpressed and no error message.

#### Scenario: Guest presses the button

- **WHEN** a guest presses 「🔔 チケット販売の通知を受け取る」 on a concert's detail sheet
- **THEN** a dialog reads 「おっと、まだアカウントを持っていないね？」 and 「通知に必要なアカウントは無料ですぐに作成できるよ！」 with 「あとで」 and 「Sign Up」
- **AND** sign-up has not started

#### Scenario: Guest chooses Sign Up

- **WHEN** the guest presses 「Sign Up」 in that dialog
- **THEN** sign-up starts

#### Scenario: Guest chooses later

- **WHEN** the guest presses 「あとで」, presses Escape or taps the backdrop
- **THEN** the dialog closes, the concert's detail sheet is still open and no sign-up has started

#### Scenario: No guest line in the ticket section

- **WHEN** a guest opens a concert's detail sheet
- **THEN** the ticket section shows no line about creating an account

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

After the level is saved, the notice SHALL read 「**{{places}}**の新着ライブをプッシュ通知します🔔」 for the new level, or 「…をプッシュ通知で受け取ろう🔔」 with the push offer when push is off for this browser (with 「Sign Up」 for a guest), and no snack SHALL appear. When the save fails, the notice SHALL stay as it was and a message SHALL say the change failed. A concert the level matches, and a concert of an artist the fan does not follow, SHALL show no notice.

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

- **WHEN** a fan opens, from the Concerts view, a concert of an artist the fan does not follow
- **THEN** no notice is shown
