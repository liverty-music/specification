# Spec Delta

## MODIFIED Requirements

### Requirement: The fan asks for a registration link by email

The sign-in help screen SHALL be reachable at `/sign-in-help` by guests and signed-in fans alike. It SHALL explain that a link to create a new passkey will be emailed to the account's address, that the link works for 1 hour, and that it should be opened on the device that will hold the new passkey. It SHALL offer one email field and a send button. On send, it SHALL call UserService.RequestPasskeyRecovery and, on success, SHALL replace the form with the same message for every address: that if an account uses this address, an email with a link has been sent. The message SHALL NOT say whether an account exists.

#### Scenario: Fan sends their address

- **WHEN** a guest types `fan@example.com` and taps send
- **THEN** the screen says an email with a link has been sent if an account uses this address, and shows no form

#### Scenario: Address with no account

- **WHEN** a guest sends an address no account uses
- **THEN** the screen shows exactly the same message as for an account's address

#### Scenario: Malformed address

- **WHEN** the typed text is not an email address
- **THEN** the screen marks the field as invalid and sends nothing
