## ADDED Requirements

### Requirement: The home sheet at sign-up cannot be closed

When the app asks for the home area because a new account needs one (stories/sign-up-or-sign-in), the `user-home-selector` SHALL open as a sheet that tapping the backdrop, pressing ESC or swiping down does not close. It SHALL close only when the person selects an area, and the selected area SHALL be the home the account is created with.

#### Scenario: Dismiss attempts at sign-up

- **WHEN** the home sheet is open at sign-up and the person taps the backdrop or presses ESC
- **THEN** the sheet stays open and no account is created

#### Scenario: Area selected at sign-up

- **WHEN** the person selects 東京都 in the home sheet at sign-up
- **THEN** the sheet closes and the account is created with home JP-13
