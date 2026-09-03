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

