## MODIFIED Requirements

### Requirement: My Home Area Preference
The system SHALL allow users to change their home area preference (prefecture) which determines the Timetable's geographical context.

#### Scenario: Opening home area selector
- **WHEN** a user taps the "My Home Area" row in Settings
- **THEN** the system SHALL display the `home-area-selector` component in a bottom sheet (the `bottom-sheet` component, a native `<dialog popover="manual">`)
- **AND** the sheet SHALL be promoted to the browser's Top Layer, rendering above all page content including the bottom navigation bar
- **AND** the sheet SHALL NOT use z-index utilities for stacking
- **AND** Step 1 SHALL show quick-select major city buttons (Tokyo, Osaka, Nagoya, Fukuoka, Sapporo, Sendai) and region buttons (Hokkaido, Tohoku, Kanto, Chubu, Kinki, Chugoku, Shikoku, Kyushu)
- **AND** WHEN a user taps a region, Step 2 SHALL show prefectures within the selected region

#### Scenario: Dialog backdrop and dismiss
- **WHEN** the home area selector sheet is open from Settings, as the Concerts view's area selector, or as the home sheet of a guest who has finished onboarding
- **THEN** the `::backdrop` pseudo-element SHALL display a dark translucent overlay with blur effect
- **AND** tapping the dimmed area SHALL close the sheet
- **AND** pressing the ESC key SHALL close the sheet

#### Scenario: Dialog open/close animation
- **WHEN** the home area selector sheet opens
- **THEN** the sheet SHALL slide up from the bottom of the viewport as every bottom sheet does (see the bottom-sheet requirement "The sheet rises from the bottom edge on entry")
- **AND** WHEN the sheet closes
- **THEN** it SHALL close by the dismiss scroll that every bottom sheet closes by
- **AND** users with `prefers-reduced-motion: reduce` SHALL see the sheet fade in over at most 100 ms without sliding, and the sheet close without sliding

#### Scenario: Changing home area
- **WHEN** a user selects a prefecture in Step 2 or a quick-select city in Step 1
- **THEN** the system SHALL update the user's home area preference
- **AND** the sheet SHALL close
- **AND** the Settings row SHALL reflect the new home area
- **AND** the Timetable SHALL use the new home area for Timetable Grid lane calculations on next load

#### Scenario: My Home Area displays from backend User entity
- **WHEN** the Settings page loads for an authenticated user
- **THEN** the My Home Area row SHALL display the home area from `UserService.current.home`
- **AND** SHALL NOT read from localStorage for home area display
- **AND** if `UserService.current.home` is absent, the row SHALL display the localized "Not set" text

---
