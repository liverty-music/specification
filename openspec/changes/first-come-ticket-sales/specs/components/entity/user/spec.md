# Spec Delta

## ADDED Requirements

### Requirement: Holder identity on the account

A User's holder full name, when present, SHALL be 1 to 200 characters, and their holder phone number, when present, SHALL be in E.164 form. Both are absent until the User first checks out.

#### Scenario: Saved identity

- **WHEN** a User's holder full name is `山田 花子` and their phone number is `+819012345678`
- **THEN** the identity is valid

#### Scenario: Domestic-format phone number

- **WHEN** a User's holder phone number is `09012345678`
- **THEN** the identity is invalid
