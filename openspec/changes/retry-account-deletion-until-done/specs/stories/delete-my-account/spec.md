# Spec Delta

## ADDED Requirements

### Requirement: A started deletion completes

Once a fan's deletion has started, the platform SHALL carry it on without the fan acting again, so signing up with the same email address after it has completed creates a new account. When it cannot complete, because something new blocks it, a failure cannot be retried or it still fails after 24 hours, an admin SHALL be told.

#### Scenario: Failure halfway

- **WHEN** a fan's deletion removed their identity and the account removal failed with a passing fault
- **THEN** once the fault has passed the account is removed, and signing up again with the same email address creates a new account with no follows, no tickets and no identity check (本人確認) result

#### Scenario: Deletion that cannot complete

- **WHEN** a fan's deletion removed their identity and the account removal still fails after 24 hours
- **THEN** an admin is told
