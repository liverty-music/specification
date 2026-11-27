# Spec Delta

## ADDED Requirements

### Requirement: A started deletion completes

Once a fan's deletion has started, the platform SHALL carry it on without the fan acting again. From the moment the account is removed, the fan's sign-in identity SHALL NOT get a new account, and once the deletion has completed, signing up with the same email address creates a new account. When it cannot complete, because something new blocks it, a failure cannot be retried or it still fails after 24 hours, an admin SHALL be told.

#### Scenario: Failure halfway

- **WHEN** a fan's deletion removed their account and removing their sign-in identity failed with a passing fault
- **THEN** once the fault has passed the identity is removed, and signing up again with the same email address creates a new account with no follows, no tickets and no identity check (本人確認) result

#### Scenario: Signing in before the identity is removed

- **WHEN** the fan signs in again after their account was removed and before their sign-in identity was
- **THEN** no account is created

#### Scenario: Deletion that cannot complete

- **WHEN** a fan's deletion removed their account and removing their sign-in identity still fails after 24 hours
- **THEN** an admin is told
