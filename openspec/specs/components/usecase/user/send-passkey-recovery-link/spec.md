# components/usecase/user/send-passkey-recovery-link Specification

## Purpose
UserUseCase.SendPasskeyRecoveryLink sends the passkey registration link for each announced passkey recovery request, so the person who asked can register a new passkey on the device in hand.

## Requirements

### Requirement: Each recovery request sends one registration link

SendPasskeyRecoveryLink SHALL run for each announced passkey recovery request, with its User. It SHALL read the User with User.Get and send the link with User.SendPasskeyRegistrationLink. When User.Get or User.SendPasskeyRegistrationLink fails with NotFound, or User.SendPasskeyRegistrationLink fails with FailedPrecondition, it SHALL log the outcome and finish without sending. Any other failure SHALL fail SendPasskeyRecoveryLink so it is run again; a run again after a link was sent sends a newer link.

#### Scenario: Fan with a verified address

- **WHEN** a recovery request is announced for a User whose identity's address is verified
- **THEN** the User receives one email with a passkey registration link

#### Scenario: Unverified address

- **WHEN** User.SendPasskeyRegistrationLink fails with FailedPrecondition
- **THEN** no email is sent, the outcome is logged and the request is finished

#### Scenario: Account deleted since the request

- **WHEN** User.Get fails with NotFound
- **THEN** no email is sent and the request is finished

#### Scenario: Mail service down

- **WHEN** User.SendPasskeyRegistrationLink fails with Internal
- **THEN** SendPasskeyRecoveryLink fails and runs again
