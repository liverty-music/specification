## Purpose

Receives the identity provider's notices that an identity signed in through the hosted sign-in, and records each one for the signed-in User with UserUseCase.RecordLogin, without ever affecting the sign-in itself.

## ADDED Requirements

### Requirement: Only authentic notices are accepted

The login-events webhook SHALL accept a notice only when it carries a valid signature made with the key shared with the identity provider for this webhook. A notice with a missing or invalid signature SHALL be rejected with HTTP 401 and SHALL record nothing. When no key is configured, every notice SHALL be answered with HTTP 503 and record nothing. The endpoint SHALL be reachable only from inside the cluster.

#### Scenario: Valid signature

- **WHEN** the identity provider sends a sign-in notice with a valid signature
- **THEN** the notice is accepted

#### Scenario: Forged notice

- **WHEN** a request arrives with a missing or invalid signature
- **THEN** it is rejected with HTTP 401 and nothing is recorded

#### Scenario: Key not configured

- **WHEN** a notice arrives while no key is configured
- **THEN** it is answered with HTTP 503 and nothing is recorded

### Requirement: Each sign-in notice is recorded for its identity

For an accepted notice that an identity signed in interactively, the webhook SHALL call UserUseCase.RecordLogin with the identity's provider user ID and the notice's time, or the time it was received when the notice has none, and SHALL answer HTTP 200. A silent session refresh and a machine sign-in are not sign-in notices. A notice of another kind, or one that names no identity or cannot be read, SHALL be logged, answered with HTTP 200 and record nothing. When RecordLogin fails, the webhook SHALL log the failure and answer HTTP 500; the identity provider does not deliver a notice again, so that sign-in is not recorded. The answer SHALL never change the outcome of the sign-in.

#### Scenario: Fan signs in

- **WHEN** an accepted notice says a fan identity signed in at 2026-10-28 12:00 JST
- **THEN** RecordLogin is called with that identity's provider user ID and 2026-10-28 12:00 JST, and the webhook answers HTTP 200

#### Scenario: Older notice arrives late

- **WHEN** a notice of a sign-in at 2026-10-28 10:00 JST arrives after one at 2026-10-28 12:00 JST was recorded for the same User
- **THEN** the webhook answers HTTP 200 and the User's last login time stays 2026-10-28 12:00 JST

#### Scenario: Notice of another kind

- **WHEN** an accepted notice is of a kind other than a sign-in
- **THEN** the webhook answers HTTP 200 and nothing is recorded

#### Scenario: Recording fails

- **WHEN** RecordLogin fails with Unavailable
- **THEN** the webhook logs the failure and answers HTTP 500, and the fan's sign-in succeeds as usual
