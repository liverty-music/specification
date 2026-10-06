# Spec Delta

## MODIFIED Requirements

### Requirement: Applicant identity is required

The applicant full name SHALL be 1-200 characters. The applicant phone number SHALL be in E.164 form: a `+` followed by 2-15 digits whose first digit is not 0, with no spaces or separators.

#### Scenario: Identity complete

- **WHEN** a full name within its length and the phone number `+819012345678` are given
- **THEN** the identity is valid

#### Scenario: Missing name or phone

- **WHEN** the full name or the phone number is empty
- **THEN** the identity is invalid

#### Scenario: Domestic-format phone number

- **WHEN** the phone number is `090-1234-5678` or `09012345678`
- **THEN** the identity is invalid

#### Scenario: Phone number too long

- **WHEN** the phone number is a `+` followed by 16 digits
- **THEN** the identity is invalid
