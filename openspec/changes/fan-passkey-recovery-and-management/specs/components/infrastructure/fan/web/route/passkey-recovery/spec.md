## Purpose

Provides the "can't sign in" screen, where a person who cannot use any of their passkeys asks for an email link that registers a new passkey on the device in hand.

## ADDED Requirements

### Requirement: The fan asks for a registration link by email

The passkey recovery screen SHALL be reachable at `/passkey-recovery` by guests and signed-in fans alike. It SHALL explain that a link to create a new passkey will be emailed to the account's address, that the link works for 1 hour, and that it should be opened on the device that will hold the new passkey. It SHALL offer one email field and a send button. On send, it SHALL call UserService.RequestPasskeyRecovery and, on success, SHALL replace the form with the same message for every address: that if an account uses this address, an email with a link has been sent. The message SHALL NOT say whether an account exists.

#### Scenario: Fan sends their address

- **WHEN** a guest types `fan@example.com` and taps send
- **THEN** the screen says an email with a link has been sent if an account uses this address, and shows no form

#### Scenario: Address with no account

- **WHEN** a guest sends an address no account uses
- **THEN** the screen shows exactly the same message as for an account's address

#### Scenario: Malformed address

- **WHEN** the typed text is not an email address
- **THEN** the screen marks the field as invalid and sends nothing

### Requirement: Resending waits 60 seconds and respects the limit

After a successful send, the screen SHALL offer to send the link again once 60 seconds have passed, counting down until then. When UserService.RequestPasskeyRecovery fails with ResourceExhausted, the screen SHALL say that too many requests were made and to try again later, and SHALL keep the typed address. Any other failure SHALL say the request could not be sent and offer to try again.

#### Scenario: Resend after 60 seconds

- **WHEN** 60 seconds have passed since a successful send
- **THEN** the screen offers to send the link again to the same address

#### Scenario: Too many requests

- **WHEN** the request fails with ResourceExhausted
- **THEN** the screen says to try again later and keeps the typed address

#### Scenario: Network failure

- **WHEN** the request fails with Unavailable
- **THEN** the screen says the request could not be sent and offers to try again
