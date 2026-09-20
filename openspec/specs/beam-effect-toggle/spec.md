# Beam Effect Toggle

## Purpose

Provides a user-controllable toggle for the laser beam spotlight visual effect on the concert highway dashboard. The preference is persisted in localStorage so the user's choice is remembered across sessions.
## Requirements
### Requirement: User can toggle the laser beam spotlight effect on the dashboard

The dashboard SHALL provide a toggle to enable or disable the laser beam spotlight
visual effect on the concert highway. The toggle SHALL be presented as an inline
toggle item within the FAB action launcher panel (see the `fab-action-launcher`
capability), not as a button in the page header. The preference SHALL be persisted
in localStorage under the key `liverty:beams:enabled`. The default state SHALL be
`false` (disabled). The toggle item SHALL be contributed to the launcher only while
the dashboard is in My Timetable mode.

#### Scenario: Default state is off on first visit

- **WHEN** a user visits the dashboard for the first time
- **AND** the `liverty:beams:enabled` key is not set in localStorage
- **THEN** the laser beam effect SHALL NOT be rendered on the concert highway
- **AND** the beam toggle item SHALL appear in its inactive (off) state

#### Scenario: Enabling the beam effect

- **WHEN** the user taps the beam toggle item while the effect is disabled
- **THEN** the laser beam spotlight overlay SHALL appear on the concert highway
- **AND** the toggle item SHALL reflect the active (on) state
- **AND** `liverty:beams:enabled` SHALL be set to `"true"` in localStorage

#### Scenario: Disabling the beam effect

- **WHEN** the user taps the beam toggle item while the effect is enabled
- **THEN** the laser beam spotlight overlay SHALL be removed from the concert highway
- **AND** the toggle item SHALL return to its inactive (off) state
- **AND** `liverty:beams:enabled` SHALL be set to `"false"` in localStorage

#### Scenario: Preference is restored on page reload

- **WHEN** the user reloads the dashboard
- **AND** `liverty:beams:enabled` is `"true"` in localStorage
- **THEN** the laser beam effect SHALL be enabled immediately on load without user interaction

#### Scenario: Toggle button placement and icon

- **WHEN** the dashboard is displayed in My Timetable mode
- **THEN** a beam toggle item SHALL be contributed to the FAB action launcher panel
- **AND** the item SHALL use the `spotlight` icon together with a text label
- **AND** the item SHALL reflect the current enabled state to assistive technology (pressed/selected)
- **AND** the beam toggle SHALL NOT be rendered as a button in the page header

### Requirement: The beam effect is presentational and costs nothing to render

The laser beam spotlight SHALL be driven by the scroll position of the concert it
is anchored to, without per-frame scripting and without reading the geometry of
any concert card. Reading card geometry to position the beams forces layout of
content the browser would otherwise skip, so it both costs main-thread time
proportional to the number of concerts and defeats viewport-scoped rendering of
the timetable.

The effect SHALL degrade to no beams where the platform cannot drive it, and its
absence SHALL change nothing else: the timetable, the toggle and the persisted
preference SHALL behave identically.

#### Scenario: Beams track scroll position without scripting

- **WHEN** the fan scrolls the timetable with the beam effect enabled
- **THEN** each beam SHALL follow its anchor concert's position
- **AND** no per-frame script SHALL read the position or size of any concert card

#### Scenario: Beams do not defeat viewport-scoped rendering

- **WHEN** the beam effect is enabled on a timetable whose off-screen date groups
  are being skipped
- **THEN** those groups SHALL remain skipped
- **AND** the beams SHALL NOT cause them to be laid out

#### Scenario: Only concerts on screen are lit

- **WHEN** the beam effect is enabled on a timetable longer than the viewport
- **THEN** only the concerts currently on screen SHALL have a beam drawn
- **AND** a concert the fan has not scrolled to SHALL NOT be lit, whether its date
  group is merely below the fold or is being skipped entirely

#### Scenario: Beams are absent where unsupported, with nothing else affected

- **WHEN** the fan's browser cannot drive the effect
- **THEN** no beams SHALL be shown
- **AND** the toggle SHALL still be offered, still persist the preference, and the
  timetable SHALL render and behave exactly as it does with the effect disabled
