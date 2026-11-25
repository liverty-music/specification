## MODIFIED Requirements

### Requirement: Two-Tier Celebration Overlay

The system SHALL present a celebration overlay at two distinct moments on the Timetable, gated on the timetable being real (home area set and data loaded). Each tier SHALL be shown at most once on the device. The light tier counts as shown once the overlay has opened. The post-signup tier counts as shown only once the post-signup dialog it leads to has opened ("The post-signup sequence survives closing the app" in the post-signup dialog), so a fan who closes the app during the celebration sees it again on the next Timetable visit.

- **Light tier** (a fan in onboarding arriving at the Timetable): shown only when the fan follows at least 1 artist AND the timetable holds at least 1 concert. It renders without confetti and shows three lines: 「タイムテーブル完成！」, 「{{artists}}組のアーティストの{{concerts}}公演が見つかりました」 (the number of followed artists and the number of concerts on the timetable) and 「タップして見てみよう」.
- **Post-signup tier** (the Timetable right after a sign-up): renders with confetti, headline 「ようこそ！もうライブは見逃さない」 and a body of two lines, 「新着ライブは」 and 「Liverty Music にお任せ！」, and on dismissal opens the post-signup dialog. A sign-up started from a concert sheet's ticket sale notification button SHALL NOT show this tier; the post-signup dialog states what follows it instead.

The English locale SHALL show equivalent texts.

#### Scenario: Celebration gated on timetable readiness

- **WHEN** the Timetable is reached during onboarding or just after sign-up
- **AND** the home area has not yet been chosen (the home-area sheet is open and the timetable is blurred)
- **THEN** the system SHALL NOT show the celebration overlay
- **AND** the system SHALL decide whether to celebrate once the home area is chosen and the timetable data has loaded

#### Scenario: Guest light celebration on first timetable

- **WHEN** a fan in onboarding who follows 5 artists reaches the Timetable for the first time
- **AND** the home area is set and the timetable holds 12 concerts
- **AND** the light celebration has not been shown on this device
- **THEN** the overlay SHALL show 「タイムテーブル完成！」, 「5組のアーティストの12公演が見つかりました」 and 「タップして見てみよう」 without confetti
- **AND** the overlay SHALL be dismissible by tap
- **AND** the light celebration SHALL not be shown again on this device

#### Scenario: Follows but no concert yet

- **WHEN** a fan in onboarding who follows at least 1 artist reaches the Timetable
- **AND** the timetable holds no concert
- **THEN** the system SHALL NOT display the light celebration
- **AND** the Timetable empty state 「新しいライブが見つかり次第、ここに並びます」 SHALL guide the fan instead

#### Scenario: No follows

- **WHEN** a fan in onboarding with no followed artist reaches the Timetable
- **THEN** the system SHALL NOT display the light celebration

#### Scenario: No light celebration for a completed guest revisiting the timetable

- **WHEN** a fan whose onboarding is already completed navigates to the Timetable
- **THEN** the system SHALL NOT display the light celebration overlay

#### Scenario: Post-signup full celebration then dialog

- **WHEN** a newly signed-up user is redirected to the Timetable with a pending post-signup celebration
- **AND** the home area is set and the timetable data has loaded
- **THEN** the system SHALL display the overlay with confetti, 「ようこそ！もうライブは見逃さない」 and the two lines 「新着ライブは」 「Liverty Music にお任せ！」
- **AND** on dismissal the system SHALL open the post-signup dialog (per `post-signup-dialog`)

#### Scenario: Sign-up from the notification button

- **WHEN** a guest presses the ticket sale notification button on a concert sheet, chooses Sign Up and completes sign-up
- **THEN** the concert's detail sheet opens on the Timetable and no celebration overlay is shown, then or later

#### Scenario: Celebration does not replay

- **WHEN** a user who has already seen a given celebration tier, as the requirement counts it, returns to the Timetable
- **THEN** the system SHALL NOT display that celebration tier again

#### Scenario: Reduced motion preference

- **WHEN** the user has a reduced-motion preference
- **THEN** either tier SHALL still appear under the same conditions, with the motion limits of "Celebration Reveals the Timetable Behind the Text"
