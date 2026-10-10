# Spec Delta

## ADDED Requirements

### Requirement: Personal details

A User's full name, when present, SHALL be 1 to 200 characters. A User's phone number, when present, SHALL be in E.164 form: a `+` followed by 2 to 15 digits whose first digit is not 0, with no spaces or separators. Both are absent until the User first gives them.

#### Scenario: Details complete
- **WHEN** a User's full name is 山田 花子 and their phone number is `+819012345678`
- **THEN** the details are valid

#### Scenario: Domestic-format phone number
- **WHEN** a User's phone number is `090-1234-5678` or `09012345678`
- **THEN** the details are invalid

#### Scenario: Phone number too long
- **WHEN** a User's phone number is a `+` followed by 16 digits
- **THEN** the details are invalid

#### Scenario: Not given yet
- **WHEN** a User has never given a full name or phone number
- **THEN** both are absent and the User is valid
