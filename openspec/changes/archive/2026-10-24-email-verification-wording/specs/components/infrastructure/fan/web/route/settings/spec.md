## MODIFIED Requirements

### Requirement: The verification badge shows the current state

For a signed-in fan, the email verification badge SHALL reflect the identity provider's current state of the address, read again each time Settings opens and each time the fan returns to its tab, not only the state at sign-in. In Japanese the badge SHALL read 確認済み for a verified address and 未確認, with the resend action, for an address that is not verified, the word the verification email and the email verification screen use. When the address has been verified since sign-in, on this device or another, the badge SHALL show 確認済み and the resend action SHALL disappear. When the state cannot be read, the badge SHALL keep the last known state.

#### Scenario: Verified on another device

- **WHEN** a fan signed in on a laptop before verifying, verifies from their phone, and returns to Settings on the laptop
- **THEN** the badge shows 確認済み and no resend action is shown

#### Scenario: Not yet verified

- **WHEN** a fan whose address is not verified opens Settings in Japanese
- **THEN** the badge shows 未確認 next to the resend action

#### Scenario: State cannot be read

- **WHEN** reading the current state fails
- **THEN** the badge keeps showing the last known state
