# Delta for my-artists

## ADDED Requirements

### Requirement: The hype dots' guide moment

When My Artists lists at least one followed artist and no followed artist has a hype level other than the default Nearby, My Artists SHALL show a guide moment on the first row's 🔥 dots, for a guest and for a signed-in fan alike, with the line 「Hype (熱量) に合わせて 🔥 を変えてみよう！」 (EN "Change the 🔥 to match your Hype!"). The dots SHALL light up from left to right without changing the level. When the home-area sheet opens on My Artists, the moment SHALL wait until the sheet closes. The fan's first hype change SHALL end it and count as using it; the hype snack then says what the level does.

#### Scenario: A guest opens My Artists
- **WHEN** a guest whose follows are all at Nearby opens My Artists and has a home area
- **THEN** the first row's 🔥 dots light up and 「Hype (熱量) に合わせて 🔥 を変えてみよう！」 is shown
- **WHEN** the guest sets that artist to Away
- **THEN** the moment ends and the hype snack for Away appears

#### Scenario: After the home-area sheet
- **WHEN** a guest without a home area opens My Artists
- **THEN** the moment appears only after the guest chooses an area and the sheet closes

#### Scenario: A fan who set a level before
- **WHEN** a signed-in fan with one artist at Away opens My Artists on a new device
- **THEN** the hype dots' moment does not appear

## MODIFIED Requirements

### Requirement: A hype change says where new concerts are pushed

When a hype level change on My Artists applies, My Artists SHALL show one snack that says, in place words, which new concerts of the artist will reach the fan by push. The place words SHALL be 「全て」 for Away, the fan's home prefecture's short name (for example 「東京」) for Home, and that name followed by 「周辺」 (for example 「東京周辺」) for Nearby; with no home area, 「HOMEエリア」 takes the place of the prefecture name. The snack SHALL read, on one line when it fits:

| when | snack | action |
|---|---|---|
| push is on for this browser, Home, Nearby or Away | 「{{name}}の{{places}}の新着ライブをプッシュ通知します🔔」 | none |
| push is on for this browser, Watch | 「{{name}}の新着ライブはプッシュ通知しません」 | none |
| push is off for this browser, Home, Nearby or Away | 「{{name}}の{{places}}の新着ライブをプッシュ通知で受け取ろう🔔」 | the push offer (stated by the notification prompt surface) |
| guest, Home, Nearby or Away | 「{{name}}の{{places}}の新着ライブをプッシュ通知で受け取ろう🔔」 | 「Sign Up」, which starts sign-up |

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
- **THEN** a snack reads 「ヨルシカの大阪の新着ライブをプッシュ通知で受け取ろう🔔」 with the action 「Sign Up」

#### Scenario: No home area

- **WHEN** a guest with no home area sets ヨルシカ to Home for the first time on this device
- **THEN** a snack reads 「ヨルシカのHOMEエリアの新着ライブをプッシュ通知で受け取ろう🔔」 with the action 「Sign Up」

#### Scenario: Quick changes to one artist

- **WHEN** a fan sets ヨルシカ to Home and then to Away within a second, and both levels are picked for the first time
- **THEN** only the snack for Away remains on screen

#### Scenario: Save fails

- **WHEN** a signed-in fan changes a hype level and saving fails twice
- **THEN** the failure message is shown and no hype snack is shown
