# Spec Delta

## ADDED Requirements

### Requirement: A deletion that stopped halfway does not block a new account

When a fan's sign-in identity was removed but their account was not, signing up again with the same email address SHALL create a new, empty account with UserUseCase.Create.

#### Scenario: Signing up after a failed deletion

- **WHEN** a fan's deletion removed their identity and failed before removing the account, and the fan signs up again with the same email address
- **THEN** a new account is created with no follows, no tickets and no identity check (本人確認) result
