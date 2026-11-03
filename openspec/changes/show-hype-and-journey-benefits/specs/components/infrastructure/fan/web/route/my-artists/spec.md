## REMOVED Requirements

### Requirement: Push offer after a hype change

**Reason**: The hype snack ("A hype change says where new concerts are pushed") says what the new level delivers and carries the push offer as its action, so a second snack after the same change is no longer shown.
**Migration**: None. The offer's wording 「{{name}}を {{hype}} にしました。新着ライブを通知で受け取りますか？」 and its translation key are removed; the hype snack replaces it.

## ADDED Requirements

### Requirement: A hype change says where new concerts are pushed

When a hype level change on My Artists applies, My Artists SHALL show one snack that says, in place words, which new concerts of the artist will reach the fan by push. The place words SHALL be 「全て」 for Away, the fan's home prefecture's short name (for example 「東京」) for Home, and that name followed by 「周辺」 (for example 「東京周辺」) for Nearby; with no home area, 「居住エリア」 takes the place of the prefecture name. The snack SHALL read, on one line when it fits:

| when | snack | action |
|---|---|---|
| push is on for this browser, Home, Nearby or Away | 「{{name}}の{{places}}の新着ライブをプッシュ通知します🔔」 | none |
| push is on for this browser, Watch | 「{{name}}の新着ライブはプッシュ通知しません」 | none |
| push is off for this browser, Home, Nearby or Away | 「{{name}}の{{places}}の新着ライブをプッシュ通知で受け取ろう🔔」 | the push offer (stated by the notification prompt surface) |
| guest, Home, Nearby or Away | 「{{name}}の{{places}}の新着ライブをプッシュ通知で受け取ろう🔔」 | 「登録する」, which starts sign-up |

The English locale SHALL show equivalent texts. Push is on for this browser when the fan allowed notifications and this browser is registered for push.

When push is on, and for a guest, the snack for a level SHALL appear only the first time the fan picks that level on this device; later picks of the same level show no snack. When push is off for a signed-in fan, the snack SHALL appear on every change, except that Watch shows no snack then. A guest picking Watch sees no snack. A change whose save fails SHALL show the failure message and no hype snack. Several changes to the same artist in a row SHALL leave only the latest snack for that artist on screen.

#### Scenario: First pick of Away with push on

- **WHEN** a signed-in fan with home JP-13 whose browser receives push sets ヨルシカ to Away for the first time on this device
- **THEN** a snack reads 「ヨルシカの全ての新着ライブをプッシュ通知します🔔」

#### Scenario: Second pick of the same level

- **WHEN** that fan later sets YOASOBI to Away
- **THEN** the change applies and no snack appears

#### Scenario: Nearby with push off

- **WHEN** a signed-in fan with home JP-13 whose notification permission is undecided sets Vaundy to Nearby, for the second time that day
- **THEN** a snack reads 「Vaundyの東京周辺の新着ライブをプッシュ通知で受け取ろう🔔」 with the push offer as its action

#### Scenario: Watch for the first time

- **WHEN** a signed-in fan whose browser receives push sets King Gnu to Watch for the first time on this device
- **THEN** a snack reads 「King Gnuの新着ライブはプッシュ通知しません」

#### Scenario: Guest picks Home

- **WHEN** a guest with home JP-27 sets ヨルシカ to Home for the first time on this device
- **THEN** a snack reads 「ヨルシカの大阪の新着ライブをプッシュ通知で受け取ろう🔔」 with the action 「登録する」

#### Scenario: Quick changes to one artist

- **WHEN** a fan sets ヨルシカ to Home and then to Away within a second, and both levels are picked for the first time
- **THEN** only the snack for Away remains on screen

#### Scenario: Save fails

- **WHEN** a signed-in fan changes a hype level and saving fails twice
- **THEN** the failure message is shown and no hype snack is shown
