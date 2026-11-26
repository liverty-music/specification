# components/infrastructure/fan/web/global/guide-moment Specification

## Purpose
A guide moment shows a fan one feature at the moment the fan needs it: a glow on the control and one short line next to it, with no dimmed screen, no steps and no button of its own. Each screen states its own moments (where, when and the line); this surface states what every moment shares.

## Requirements

### Requirement: A guide moment is a glow and one line that never blocks

A guide moment SHALL light the edge of its target control and show one line of text next to it. It SHALL NOT dim the screen, lock scrolling, add a button or take taps: a tap on the target performs the target's own action, and a tap anywhere else reaches the page beneath. The line SHALL be announced to assistive technology as a status message. With a reduced-motion preference the glow SHALL be steady and nothing SHALL bounce, shake or light up in sequence; the line SHALL still show.

#### Scenario: The page stays usable
- **WHEN** a guide moment is shown on Discovery's swap tile
- **THEN** the screen is not dimmed, the page scrolls, and a tap on a bubble follows that artist

#### Scenario: Tapping the target performs its action
- **WHEN** the fan taps the glowing swap tile
- **THEN** Discovery switches to the Concerts view, as a tap without the moment would

#### Scenario: Screen reader
- **WHEN** a guide moment appears
- **THEN** a screen reader announces its line once

#### Scenario: Reduced motion
- **WHEN** a fan with a reduced-motion preference gets a guide moment
- **THEN** the target has a steady glow with no motion and the line is shown

### Requirement: One guide moment at a time, never over another interruption

At most one guide moment SHALL be shown at a time. A guide moment SHALL NOT appear while a bottom sheet, a dialog, the celebration overlay or the post-signup dialog is open, except a moment whose target is inside the open concert sheet. A moment that was due while such a surface was open SHALL appear once, after that surface closes, if the fan is still on the same screen. When two moments are due at once, the one whose screen is shown SHALL appear and the other SHALL wait for its own conditions again.

#### Scenario: Home-area sheet open
- **WHEN** a moment on My Artists becomes due while the home-area sheet is open
- **THEN** the moment does not appear until the sheet closes, and then appears once

#### Scenario: A dialog over the concert sheet
- **WHEN** a guest presses the 🔔 button and the sign-up dialog opens over the concert sheet
- **THEN** no guide moment is shown while the dialog is open

#### Scenario: Inside the concert sheet
- **WHEN** the concert sheet opens and its own moment is due
- **THEN** the moment appears inside the sheet

### Requirement: A guide moment ends when the fan acts or moves on

A guide moment SHALL end when the fan uses its target, taps anywhere outside it, or leaves the screen, or when a bottom sheet, a dialog, the celebration overlay or the post-signup dialog opens over it, and SHALL leave nothing on screen. A moment that such a surface ended before it counted as seen SHALL appear once more after the surface closes, if the fan is still on the same screen.

#### Scenario: Tap elsewhere
- **WHEN** the fan taps outside the target of a shown moment
- **THEN** the glow and the line disappear and the tap reaches the page

#### Scenario: Leaving the screen
- **WHEN** the fan leaves the screen while a moment is shown
- **THEN** no glow or line remains on the next screen

#### Scenario: A sheet opens over a shown moment
- **WHEN** a sheet opens over a moment that has been on screen for less than 3 seconds
- **THEN** the glow and the line disappear, and the moment appears again once the sheet closes

### Requirement: Each guide moment is shown once per device and survives sign-up

Each guide moment SHALL be shown at most once on a device. It SHALL count as seen once the fan used its target, or once it stayed on screen for 3 seconds; a moment that ended sooner by a tap elsewhere, by leaving the screen or by a surface opening over it SHALL NOT count as seen. Seen moments SHALL stay seen through sign-up, sign-in and the reset of a guest's local data. A screen's own condition (for example the fan's follows or journeys) SHALL keep a moment from showing to a fan who already uses the feature, on any device.

#### Scenario: Seen after 3 seconds
- **WHEN** a moment stays on screen for 3 seconds and the fan then leaves the screen
- **THEN** the moment does not appear again on this device

#### Scenario: Left at once
- **WHEN** a moment appears and the fan leaves the screen within 1 second
- **THEN** the moment can appear again on the fan's next visit to that screen

#### Scenario: Sign-up keeps seen moments
- **WHEN** a guest who saw the bubble-field moment signs up and opens Discovery
- **THEN** the bubble-field moment does not appear again

### Requirement: Help replays a guide moment

A help section that has a guide moment SHALL offer a 「チュートリアル」 (EN "Show me") button while that moment's target is on the screen, and no button while it is not (the bubble field on the Concerts view, the 🔥 dots with no followed artist). Pressing it SHALL close help and show that moment on the current screen whether or not it was seen, under the rules of this surface except that the screen's own condition is not checked.

#### Scenario: Replay the hype moment
- **WHEN** a fan who has set hype levels before opens My Artists help and presses 「チュートリアル」 in the Hype section
- **THEN** help closes and the hype moment appears on the 🔥 dots

### Requirement: Guide moments are reported

The fan app SHALL send one usage analytics event when a guide moment appears, one when the fan uses its target, and one when it ends otherwise, each naming the moment, whether the fan is a guest, and whether the fan is in onboarding; the ending event SHALL also say why it ended: a tap elsewhere, leaving the screen, or a sheet, dialog or celebration opening over it. A moment kept from appearing by such a blocker sends no event until it appears.

#### Scenario: Moment used
- **WHEN** the swap-tile moment appears and the fan taps the tile
- **THEN** one event reports the moment shown and one reports it used, both naming the swap-tile moment

### Requirement: The guide line fades in and out

The guide line SHALL fade in when it opens and fade out when it closes, over the `md.sys.spring.effects` duration (200 ms) with the effects spring's curve, instead of appearing and vanishing at once. Under reduced motion it fades over at most 100 ms.

#### Scenario: The guide line closes with a fade

- **WHEN** the guide line is showing and its moment ends
- **THEN** the line fades out over 200 ms and is then no longer rendered

### Requirement: The line stays on screen at an edge

When the guide line's target is near the left or right edge of the screen, the line SHALL stay inside the screen with at least 8 px to either edge (M3 tooltips keep 8 dp from the screen's edges).

#### Scenario: The line stays on screen at an edge

- **WHEN** the guide line points at a target at the end of a 320 px phone's row
- **THEN** the line is at least 8 px from both edges of the screen
