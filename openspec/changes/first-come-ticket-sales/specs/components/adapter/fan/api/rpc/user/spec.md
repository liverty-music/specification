# Spec Delta

## MODIFIED Requirements

### Requirement: A returned user shows the profile fields

Every user service call that returns a User SHALL return its id, email, external id, name, preferred language when set, home as country code, level 1 and, when set, level 2, and the 本人確認 (identity check) holder full name and phone number when set, which the checkout prefills. It SHALL NOT return the home's centroid or a verification level.

#### Scenario: User with home and language

- **WHEN** a call returns a User with preferred language `ja` and home `JP-13`
- **THEN** the response carries preferred language `ja` and home country code `JP`, level 1 `JP-13`, without a centroid

#### Scenario: User without optional values

- **WHEN** a call returns a User with no preferred language, no home and no holder identity
- **THEN** the response carries none of them

#### Scenario: Returning buyer

- **WHEN** Get returns a User who checked out before as `山田 花子` with phone number `+819012345678`
- **THEN** the response carries that holder full name and phone number
