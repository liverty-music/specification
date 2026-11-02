## Purpose

UserUseCase.RecordLogin records a sign-in that the identity provider reported for an identity, as the signed-in User's last login time, so product analytics counts each fan's sign-ins.

## ADDED Requirements

### Requirement: A reported sign-in is recorded for its User

RecordLogin SHALL take an identity's provider user ID and the time of its sign-in. It SHALL read the User with User.GetByProviderUserID and record the sign-in with User.RecordLogin. When no User has the provider user ID, or User.RecordLogin fails with NotFound because the User was deleted after it was read, RecordLogin SHALL succeed and record nothing. Any other failure SHALL fail RecordLogin with that failure's error.

#### Scenario: Fan signs in

- **WHEN** RecordLogin runs for the provider user ID of a User with the time 2026-10-28 12:00 JST
- **THEN** User.RecordLogin runs for that User with 2026-10-28 12:00 JST

#### Scenario: Identity with no account

- **WHEN** no User has the provider user ID, as for a sign-in before sign-up finished
- **THEN** RecordLogin succeeds and nothing is recorded

#### Scenario: Store unavailable

- **WHEN** User.RecordLogin fails with Unavailable
- **THEN** RecordLogin fails with Unavailable
