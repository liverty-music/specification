# Spec Delta

## ADDED Requirements

### Requirement: A started deletion completes

Once a fan's deletion has started, the platform SHALL complete it without the fan acting again, so signing up later with the same email address creates a new account.

#### Scenario: Failure halfway

- **WHEN** a fan's deletion removed their identity and the account removal failed with a passing fault
- **THEN** the account is removed shortly afterwards, and signing up again with the same email address creates a new account with no follows, no tickets and no identity check (本人確認) result
