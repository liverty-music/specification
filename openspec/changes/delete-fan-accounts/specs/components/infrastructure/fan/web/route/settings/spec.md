## MODIFIED Requirements

### Requirement: Sign Out
The system SHALL allow authenticated users to sign out of their account. The Sign Out control SHALL be rendered only when the user is authenticated and SHALL be hidden for guest (unauthenticated) users. It SHALL stand apart from every other control, in a group of its own below the ACCOUNT section with at least 24px between them, so a tap meant for an account row never signs the user out. Only the Delete account control SHALL come after it.

#### Scenario: Sign out action
- **WHEN** an authenticated user taps the "Sign Out" button
- **THEN** the system SHALL clear the user's authentication session
- **AND** the system SHALL navigate to the Landing Page
- **AND** the Sign Out button SHALL be visually distinct (e.g., red text) and positioned at the bottom of the settings list, above only the Delete account control

#### Scenario: Sign out apart from account rows
- **WHEN** an authenticated user views the ACCOUNT section with the Passkeys row as its last row
- **THEN** the Sign Out control SHALL be in a separate group below it, at least 24px away, not adjoining the Passkeys row

#### Scenario: Sign out hidden for guests
- **WHEN** an unauthenticated (guest) user views the Settings page
- **THEN** the system SHALL NOT render the Sign Out control

## ADDED Requirements

### Requirement: Delete account entry below Sign Out

For a signed-in fan, Settings SHALL show a 「アカウントを削除」 (Delete account) control below the Sign Out control, in a group of its own at least 24px away from it, that opens the withdrawal screen. It SHALL NOT be shown to a guest.

#### Scenario: Signed-in fan

- **WHEN** a signed-in fan views Settings
- **THEN** the Delete account control is shown below Sign Out, apart from it, and opens the withdrawal screen

#### Scenario: Guest

- **WHEN** a guest views Settings
- **THEN** no Delete account control is shown
