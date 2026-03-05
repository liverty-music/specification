## MODIFIED Requirements

### Requirement: My Area Preference

The system SHALL allow users to change their home area preference (prefecture) which determines the Live Highway Dashboard's geographical context.

#### Scenario: Opening home area selector

- **WHEN** a user taps the "My Home Area" row in Settings
- **THEN** the system SHALL display the `user-home-selector` component as a native `<dialog>` element via `showModal()`
- **AND** the dialog SHALL be promoted to the browser's Top Layer, rendering above all page content including the bottom navigation bar
- **AND** the dialog SHALL NOT use z-index utilities for stacking
- **AND** Step 1 SHALL show quick-select major city buttons (Tokyo, Osaka, Nagoya, Fukuoka, Sapporo, Sendai) and region buttons (Hokkaido, Tohoku, Kanto, Chubu, Kinki, Chugoku, Shikoku, Kyushu)
- **AND** WHEN a user taps a region, Step 2 SHALL show prefectures within the selected region

#### Scenario: Dialog backdrop and dismiss

- **WHEN** the home area selector dialog is open
- **THEN** the `::backdrop` pseudo-element SHALL display a dark translucent overlay with blur effect
- **AND** tapping the backdrop area SHALL close the dialog
- **AND** pressing the ESC key SHALL close the dialog

#### Scenario: Dialog open/close animation

- **WHEN** the home area selector dialog opens
- **THEN** the dialog panel SHALL slide up from the bottom of the viewport with a fade-in (300ms ease-out)
- **AND** WHEN the dialog closes
- **THEN** the panel SHALL slide down with a fade-out (300ms ease-out)
- **AND** users with `prefers-reduced-motion: reduce` SHALL see instant open/close without animation

#### Scenario: Changing home area

- **WHEN** a user selects a prefecture in Step 2 or a quick-select city in Step 1
- **THEN** the system SHALL update the user's home area preference
- **AND** the dialog SHALL close
- **AND** the Settings row SHALL reflect the new home area
- **AND** the Dashboard SHALL use the new home area for Live Highway lane calculations on next load

## RENAMED Requirements

### Requirement: My Area Preference
- **FROM:** My Area Preference
- **TO:** My Home Area Preference
