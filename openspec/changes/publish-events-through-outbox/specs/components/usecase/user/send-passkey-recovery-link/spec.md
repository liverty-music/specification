## MODIFIED Requirements

### Requirement: Each recovery request sends one registration link

SendPasskeyRecoveryLink SHALL run when UserUseCase.RequestPasskeyRecovery starts it, with the User whose address was given. It SHALL read the User with User.Get and send the link with User.SendPasskeyRegistrationLink. When User.Get or User.SendPasskeyRegistrationLink fails with NotFound, or User.SendPasskeyRegistrationLink fails with FailedPrecondition, it SHALL log the outcome and finish without sending. A step that fails with Unavailable SHALL be tried again; a step tried again after a link was sent sends a newer link. Any other failure SHALL end SendPasskeyRecoveryLink with that failure, and it is reported for an admin.

#### Scenario: Fan with a verified address

- **WHEN** RequestPasskeyRecovery starts SendPasskeyRecoveryLink for a User whose identity's address is verified
- **THEN** the User receives one email with a passkey registration link

#### Scenario: Unverified address

- **WHEN** User.SendPasskeyRegistrationLink fails with FailedPrecondition
- **THEN** no email is sent, the outcome is logged and the request is finished

#### Scenario: Account deleted since the request

- **WHEN** User.Get fails with NotFound
- **THEN** no email is sent and the request is finished

#### Scenario: Mail service down

- **WHEN** User.SendPasskeyRegistrationLink fails with Unavailable
- **THEN** the step is tried again and the link is sent once the service answers

#### Scenario: Mail service refuses

- **WHEN** User.SendPasskeyRegistrationLink fails with Internal
- **THEN** SendPasskeyRecoveryLink ends with that failure and is reported for an admin
