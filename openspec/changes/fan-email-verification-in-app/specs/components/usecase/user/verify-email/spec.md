## Purpose

UserUseCase.VerifyEmail lets the person holding a verification link confirm that User's address without signing in, without revealing whether the User exists, and with limits that keep anyone from guessing codes.

## ADDED Requirements

### Requirement: The link's User and code verify the address

VerifyEmail SHALL take a User id, a code and the client's network address. It SHALL read the User with User.Get and confirm the address with User.VerifyEmail for the User's provider user ID. It SHALL succeed when the address is verified. When User.Get fails with NotFound, or User.VerifyEmail fails with InvalidArgument or NotFound, it SHALL fail with InvalidArgument, so an unknown User and a wrong, expired or used code fail alike. When User.VerifyEmail fails with Unavailable, VerifyEmail SHALL fail with Unavailable.

#### Scenario: Link from the email

- **WHEN** VerifyEmail runs with a User's id and the code from that User's latest verification email
- **THEN** the User's address is verified and the call succeeds

#### Scenario: Unknown User

- **WHEN** VerifyEmail runs with an id no User has
- **THEN** it fails with InvalidArgument, the same as for a wrong code

#### Scenario: Expired or used link

- **WHEN** User.VerifyEmail fails with InvalidArgument
- **THEN** VerifyEmail fails with InvalidArgument

#### Scenario: Identity provider down

- **WHEN** User.VerifyEmail fails with Unavailable
- **THEN** VerifyEmail fails with Unavailable

### Requirement: Attempts per client and per User are limited

VerifyEmail SHALL accept at most 10 attempts from one client and at most 5 attempts for one User id in any 60 minutes, counting every attempt whatever its outcome and whether or not a User has the id. A further attempt SHALL fail with ResourceExhausted and SHALL NOT reach User.Get or User.VerifyEmail.

#### Scenario: Sixth attempt for one User

- **WHEN** 5 attempts were made for a User id in the last 60 minutes and a sixth arrives
- **THEN** it fails with ResourceExhausted and nothing is verified

#### Scenario: Eleventh attempt from one client

- **WHEN** one client made 10 attempts in the last 60 minutes and makes another
- **THEN** it fails with ResourceExhausted
