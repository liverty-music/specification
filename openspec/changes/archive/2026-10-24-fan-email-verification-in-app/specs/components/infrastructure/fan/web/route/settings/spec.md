## ADDED Requirements

### Requirement: The verification badge shows the current state

For a signed-in fan, the email verification badge SHALL reflect the identity provider's current state of the address, read again each time Settings opens and each time the fan returns to its tab, not only the state at sign-in. When the address has been verified since sign-in, on this device or another, the badge SHALL show 認証済み and the resend action SHALL disappear. When the state cannot be read, the badge SHALL keep the last known state.

#### Scenario: Verified on another device

- **WHEN** a fan signed in on a laptop before verifying, verifies from their phone, and returns to Settings on the laptop
- **THEN** the badge shows 認証済み and no resend action is shown

#### Scenario: State cannot be read

- **WHEN** reading the current state fails
- **THEN** the badge keeps showing the last known state
