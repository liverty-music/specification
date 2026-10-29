## MODIFIED Requirements

### Requirement: A verification email follows every new user

User.Create announces each new User it stores (components/entity/user/create); Create itself SHALL announce nothing. Each announced new User SHALL cause User.SendVerification to run for that User's provider user ID; when Create returns an existing User, nothing is announced or sent. A failed send SHALL be retried up to 3 more times and then given up, and the User stays created. When User.Create fails with Unavailable because the new User cannot be announced, Create SHALL fail with Unavailable and no User is stored. When email verification is not configured, the announcement is accepted and no email is sent.

#### Scenario: New user

- **WHEN** Create stores a new User
- **THEN** a verification email is sent to the User's address

#### Scenario: User already existed

- **WHEN** Create returns an already registered User
- **THEN** no verification email is sent

#### Scenario: Sending keeps failing

- **WHEN** sending the verification email fails on the first attempt and on 3 retries
- **THEN** the send is given up and the User stays created

#### Scenario: Announcing fails

- **WHEN** User.Create fails with Unavailable because the new User cannot be announced
- **THEN** Create fails with Unavailable, no User is stored and no verification email is sent

#### Scenario: Verification not configured

- **WHEN** a new User is announced while email verification is not configured
- **THEN** no email is sent and the User stays created
