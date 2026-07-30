# Beam Effect Toggle

## Purpose

Provides a user-controllable toggle for the laser beam spotlight visual effect on the concert highway dashboard. The preference is persisted in localStorage so the user's choice is remembered across sessions.

## Requirements

### Requirement: User can toggle the laser beam spotlight effect on the dashboard

The dashboard SHALL provide a toggle button in the page header to enable or disable the laser beam spotlight visual effect on the concert highway. The preference SHALL be persisted in localStorage under the key `liverty:beams:enabled`. The default state SHALL be `false` (disabled). The toggle button SHALL be placed adjacent to the filter button in the page header slot.

#### Scenario: Default state is off on first visit

- **WHEN** a user visits the dashboard for the first time
- **AND** the `liverty:beams:enabled` key is not set in localStorage
- **THEN** the laser beam effect SHALL NOT be rendered on the concert highway
- **AND** the toggle button SHALL appear in its inactive (off) state

#### Scenario: Enabling the beam effect

- **WHEN** the user taps the beam toggle button while the effect is disabled
- **THEN** the laser beam spotlight overlay SHALL appear on the concert highway
- **AND** the toggle button SHALL reflect the active (on) state visually (brand color)
- **AND** `liverty:beams:enabled` SHALL be set to `"true"` in localStorage

#### Scenario: Disabling the beam effect

- **WHEN** the user taps the beam toggle button while the effect is enabled
- **THEN** the laser beam spotlight overlay SHALL be removed from the concert highway
- **AND** the toggle button SHALL return to its inactive (off) state
- **AND** `liverty:beams:enabled` SHALL be set to `"false"` in localStorage

#### Scenario: Preference is restored on page reload

- **WHEN** the user reloads the dashboard
- **AND** `liverty:beams:enabled` is `"true"` in localStorage
- **THEN** the laser beam effect SHALL be enabled immediately on load without user interaction

#### Scenario: Toggle button placement and icon

- **WHEN** the dashboard header is rendered
- **THEN** a spotlight icon button SHALL appear in the page header between the filter trigger and the page-help button
- **AND** the button SHALL use the `spotlight` SVG icon
- **AND** the button SHALL share the same pill-shaped border styling as the adjacent filter trigger button
- **AND** the button SHALL carry `aria-pressed` reflecting the current enabled state
