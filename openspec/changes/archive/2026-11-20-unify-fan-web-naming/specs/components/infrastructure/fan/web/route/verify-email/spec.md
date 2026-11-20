# Spec Delta

## ADDED Requirements

### Requirement: The screen's address

The screen a verification email's link opens SHALL be served at `/verify-email?user=<userId>&code=<code>`.

#### Scenario: The screen's address
- **WHEN** a fan opens the link in a verification email
- **THEN** the app shows the verification screen at `/verify-email` with the link's `user` and `code`
