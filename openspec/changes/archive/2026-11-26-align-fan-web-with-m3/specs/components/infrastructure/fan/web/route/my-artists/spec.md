## ADDED Requirements

### Requirement: Edit mode and the list's edits are animated

Entering and leaving edit mode, removing an artist and restoring it with "undo" SHALL each run as one View Transition on the artists' rows and the Done bar, so a row fades out or in, the rows around it move to their new places, the dots and the remove button cross-fade, and the Done bar fades in and out, instead of changing in one frame. The header and the bottom navigation SHALL NOT dip in opacity during it. Where the browser has no View Transitions, and under reduced motion, the edit is made at once.

#### Scenario: Undo restores a row without a jump

- **WHEN** the fan presses "undo" after removing an artist
- **THEN** the artist's row fades in at its old place while the rows below move down to make room
- **AND** edit mode is back on, as before

#### Scenario: Entering edit mode

- **WHEN** the fan enters edit mode
- **THEN** each row's dots cross-fade to its remove button and the Done bar fades in

## MODIFIED Requirements

### Requirement: Signup Banner on My Artists

The My Artists page SHALL display a persistent fixed banner above the bottom navigation bar prompting unauthenticated users to sign up. The banner SHALL be visible for any guest user on the My Artists page, regardless of onboarding state.

#### Scenario: Banner appears for guest user during onboarding

- **WHEN** an unauthenticated user views the My Artists page
- **AND** the user is in the My Artists onboarding step (or any earlier step that has progressed to this page)
- **THEN** the system SHALL display the signup-prompt-banner
- **AND** the banner SHALL be present from the moment the artist list has finished loading

#### Scenario: Banner appears for guest user after onboarding

- **WHEN** an unauthenticated user views the My Artists page
- **AND** the user has completed onboarding (`onboarding.isCompleted` is true)
- **THEN** the system SHALL display the signup-prompt-banner

#### Scenario: Banner not shown for authenticated users

- **WHEN** an authenticated user views the My Artists page
- **THEN** the signup banner SHALL NOT be shown: it is hidden and inert

#### Scenario: Banner disappears after signup

- **WHEN** the user completes signup (isAuthenticated becomes true) while on the My Artists page
- **THEN** the signup banner SHALL slide out and stay hidden and inert
