## MODIFIED Requirements

### Requirement: My Area Preference
The system SHALL allow users to change their local area preference (prefecture) which determines the Live Highway Dashboard's geographical context. The preference is stored locally on the device and is not synchronized across devices.

#### Scenario: Opening area selector
- **WHEN** a user taps the "My Area" row in Settings
- **THEN** the system SHALL display a native `<dialog>` element via `showModal()` with a 2-step selection UI
- **AND** the dialog SHALL be promoted to the browser's Top Layer, rendering above all page content including the bottom navigation bar
- **AND** the dialog SHALL NOT use z-index utilities for stacking
- **AND** Step 1 SHALL show regions (e.g., Hokkaido, Tohoku, Kanto, Chubu, Kinki, Chugoku, Shikoku, Kyushu)
- **AND** Step 2 SHALL show prefectures within the selected region

#### Scenario: Dialog backdrop and dismiss
- **WHEN** the area selector dialog is open
- **THEN** the `::backdrop` pseudo-element SHALL display a dark translucent overlay with blur effect
- **AND** tapping the backdrop area SHALL close the dialog
- **AND** pressing the ESC key SHALL close the dialog

#### Scenario: Dialog open/close animation
- **WHEN** the area selector dialog opens
- **THEN** the dialog panel SHALL slide up from the bottom of the viewport with a fade-in (300ms ease-out)
- **AND** WHEN the dialog closes
- **THEN** the panel SHALL slide down with a fade-out (300ms ease-out)
- **AND** users with `prefers-reduced-motion: reduce` SHALL see instant open/close without animation

#### Scenario: Changing area
- **WHEN** a user selects a prefecture in Step 2
- **THEN** the system SHALL update the user's local area preference
- **AND** the dialog SHALL close
- **AND** the Settings row SHALL reflect the new area
- **AND** the Dashboard SHALL use the new area for Live Highway lane calculations on next load
