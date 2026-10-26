## MODIFIED Requirements

### Requirement: Two-Tier Celebration Overlay

The system SHALL present a celebration overlay at two distinct moments on the Dashboard, gated on the timetable being real (home area set and data loaded). Each tier SHALL be shown at most once on the device.

- **Light tier** (a fan in onboarding arriving at the Dashboard): shown only when the fan follows at least 1 artist AND the timetable holds at least 1 concert. It renders without confetti and shows three lines: 「タイムテーブル完成！」, 「{{artists}}組のアーティストの{{concerts}}公演が見つかりました」 (the number of followed artists and the number of concerts on the timetable) and 「タップして見てみよう」.
- **Post-signup tier** (the Dashboard right after a sign-up): renders with confetti, headline 「ようこそ！もうライブは見逃さない」 and body 「新着ライブは、Liverty Music が追いかけます！」, and on dismissal opens the post-signup dialog.

The English locale SHALL show equivalent texts.

#### Scenario: Celebration gated on timetable readiness

- **WHEN** the Dashboard is reached during onboarding or just after sign-up
- **AND** the home area has not yet been chosen (the home-area sheet is open and the timetable is blurred)
- **THEN** the system SHALL NOT show the celebration overlay
- **AND** the system SHALL decide whether to celebrate once the home area is chosen and the timetable data has loaded

#### Scenario: Guest light celebration on first dashboard

- **WHEN** a fan in onboarding who follows 5 artists reaches the Dashboard for the first time
- **AND** the home area is set and the timetable holds 12 concerts
- **AND** the light celebration has not been shown on this device
- **THEN** the overlay SHALL show 「タイムテーブル完成！」, 「5組のアーティストの12公演が見つかりました」 and 「タップして見てみよう」 without confetti
- **AND** the overlay SHALL be dismissible by tap
- **AND** the light celebration SHALL not be shown again on this device

#### Scenario: Follows but no concert yet

- **WHEN** a fan in onboarding who follows at least 1 artist reaches the Dashboard
- **AND** the timetable holds no concert
- **THEN** the system SHALL NOT display the light celebration
- **AND** the Dashboard empty state 「新しいライブが見つかり次第、ここに並びます」 SHALL guide the fan instead

#### Scenario: No follows

- **WHEN** a fan in onboarding with no followed artist reaches the Dashboard
- **THEN** the system SHALL NOT display the light celebration

#### Scenario: No light celebration for a completed guest revisiting the dashboard

- **WHEN** a fan whose onboarding is already completed navigates to the Dashboard
- **THEN** the system SHALL NOT display the light celebration overlay

#### Scenario: Post-signup full celebration then dialog

- **WHEN** a newly signed-up user is redirected to the Dashboard with a pending post-signup celebration
- **AND** the home area is set and the timetable data has loaded
- **THEN** the system SHALL display the overlay with confetti, 「ようこそ！もうライブは見逃さない」 and 「新着ライブは、Liverty Music が追いかけます！」
- **AND** on dismissal the system SHALL open the post-signup dialog (per `post-signup-dialog`)

#### Scenario: Celebration does not replay

- **WHEN** a user who has already seen a given celebration tier returns to the Dashboard
- **THEN** the system SHALL NOT display that celebration tier again

#### Scenario: Reduced motion preference

- **WHEN** the user has a reduced-motion preference
- **THEN** either tier SHALL still appear under the same conditions, with the motion limits of "Celebration Reveals the Timetable Behind the Text"

### Requirement: Celebration Reveals the Timetable Behind the Text

The celebration overlay SHALL make its own text the only text the fan can read. Behind the overlay, the timetable or the Dashboard empty state SHALL be dimmed and blurred so that none of its text can be read through the overlay, while the shapes and colors of the timetable stay faintly visible. The headline SHALL enter by scaling up past its full size and settling back to it.

On the post-signup tier the overlay SHALL also:

- burst confetti from the centre of the screen outward, with pieces of varied size, shape, speed and rotation;
- play one short celebratory sound, following the app's sound mute setting (no sound when muted);
- vibrate briefly once on devices that support vibration.

The sound and the vibration SHALL be given only where the browser allows them, which is once the fan has interacted with the page. A fan who arrives straight from the sign-up redirect, without a tap on the page since, SHALL see the confetti and the headline without sound or vibration; a fan who chose the home area on arrival has tapped and SHALL get both.

With a reduced-motion preference the overlay SHALL show no confetti, no scaling and no vibration, and SHALL appear and disappear without transition. Tier gating, once-per-tier behaviour and tap-to-dismiss are defined by "Two-Tier Celebration Overlay".

#### Scenario: Empty-state text behind the post-signup celebration cannot be read

- **WHEN** the post-signup celebration is shown over the Dashboard empty state
- **THEN** the empty-state text SHALL NOT be readable through the overlay
- **AND** the headline and body of the celebration SHALL be fully legible

#### Scenario: Heading and sub-text stay legible over bright cards

- **WHEN** the light celebration is shown over bright timetable cards
- **THEN** the card colors SHALL remain faintly visible
- **AND** no card text SHALL be readable through the overlay
- **AND** the three celebration lines SHALL be fully legible

#### Scenario: Timetable colors remain visible at the screen edges

- **WHEN** the celebration overlay is displayed over the loaded timetable
- **THEN** the timetable's card colors SHALL remain faintly visible at the screen edges
- **AND** no timetable text SHALL be readable through the overlay

#### Scenario: Existing celebration behavior is preserved

- **WHEN** the celebration overlay is shown in either tier
- **THEN** tier gating, at-most-once-per-tier behaviour and tap-to-dismiss SHALL follow "Two-Tier Celebration Overlay"

#### Scenario: Post-signup confetti, sound and vibration

- **WHEN** the post-signup celebration appears on a device that supports vibration, with sound not muted
- **THEN** confetti SHALL burst outward from the centre with pieces of varied size, shape, speed and rotation
- **AND** the headline SHALL scale up past its full size and settle
- **AND** one short celebratory sound SHALL play
- **AND** the device SHALL vibrate briefly once

#### Scenario: No sound or vibration before the fan has touched the page

- **WHEN** the post-signup celebration appears on a page the fan has not tapped since the sign-up redirect
- **THEN** confetti SHALL burst and the headline SHALL scale up and settle
- **AND** no sound SHALL play and the device SHALL NOT vibrate

#### Scenario: Muted sound

- **WHEN** the post-signup celebration appears while the app's sound is muted
- **THEN** no sound SHALL play
- **AND** the confetti and headline animation SHALL still run

#### Scenario: Reduced motion preference

- **WHEN** the user has a reduced-motion preference
- **THEN** no confetti, no headline scaling and no vibration SHALL occur
- **AND** the overlay SHALL appear and disappear without transition animation
