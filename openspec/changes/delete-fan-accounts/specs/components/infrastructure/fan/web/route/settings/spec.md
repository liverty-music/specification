## ADDED Requirements

### Requirement: Delete account entry below Sign Out

For a signed-in fan, Settings SHALL show a 「アカウントを削除」 (Delete account) control below the Sign Out control, in a group of its own at least 24px away from it, that opens the withdrawal screen. It SHALL NOT be shown to a guest.

#### Scenario: Signed-in fan

- **WHEN** a signed-in fan views Settings
- **THEN** the Delete account control is shown below Sign Out, apart from it, and opens the withdrawal screen

#### Scenario: Guest

- **WHEN** a guest views Settings
- **THEN** no Delete account control is shown
