## ADDED Requirements

### Requirement: The scrim fades in with the celebration

The celebration's dark, blurred scrim SHALL fade in over the `md.sys.motion.duration.medium4` duration (400 ms) with the `md.sys.motion.easing.standard` easing when the celebration opens, in step with its fade-out on exit, instead of appearing at full strength while its text animates in. Under reduced motion the scrim fades over at most 100 ms.

#### Scenario: The celebration opens

- **WHEN** the celebration opens
- **THEN** the scrim starts transparent and reaches its full strength over 400 ms while the text animates in

## MODIFIED Requirements

### Requirement: Celebration Reveals the Timetable Behind the Text

The celebration overlay SHALL make its own text the only text the fan can read. Behind the overlay, the timetable or the Timetable empty state SHALL be dimmed and blurred so that none of its text can be read through the overlay, while the shapes and colors of the timetable stay faintly visible. The headline SHALL enter by scaling up past its full size and settling back to it.

On the post-signup tier the overlay SHALL also:

- burst confetti from the centre of the screen outward, with pieces of varied size, shape, speed and rotation;
- play one short celebratory sound, following the app's sound mute setting (no sound when muted);
- vibrate briefly once on devices that support vibration.

The sound and the vibration SHALL be given only where the browser allows them, which is once the fan has interacted with the page. A fan who arrives straight from the sign-up redirect, without a tap on the page since, SHALL see the confetti and the headline without sound or vibration; a fan who chose the home area on arrival has tapped and SHALL get both.

With a reduced-motion preference the overlay SHALL show no confetti, no scaling and no vibration, and SHALL fade in and out over at most 100 ms. Tier gating, once-per-tier behaviour and tap-to-dismiss are defined by "Two-Tier Celebration Overlay".

#### Scenario: Empty-state text behind the post-signup celebration cannot be read

- **WHEN** the post-signup celebration is shown over the Timetable empty state
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
- **AND** the overlay SHALL fade in and out over at most 100 ms, without movement
