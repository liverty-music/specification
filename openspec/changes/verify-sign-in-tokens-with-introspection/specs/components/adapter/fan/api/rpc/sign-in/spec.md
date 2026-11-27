# Spec Delta

## Purpose

Which sign-in the fan API accepts on a call that needs one: an active access token issued for the fan app, checked with the sign-in service.

## ADDED Requirements

### Requirement: Only an active access token is a sign-in

On a call that needs a sign-in, the fan API SHALL accept only an access token that is signed by the sign-in service, unexpired and reported active by it. It SHALL refuse every other token with Unauthenticated, an ID token included, and SHALL read and change nothing.

#### Scenario: Access token

- **WHEN** a caller calls with an active access token issued for the fan app
- **THEN** the call is handled

#### Scenario: ID token

- **WHEN** a caller calls with an unexpired ID token issued for the fan app
- **THEN** the call fails with Unauthenticated and nothing is read or changed

#### Scenario: Removed identity

- **WHEN** a caller calls with an unexpired access token of an identity removed more than 60 seconds ago
- **THEN** the call fails with Unauthenticated

### Requirement: A token for another app is refused

The fan API SHALL refuse with PermissionDenied, reading and changing nothing, a token the sign-in service issued that is not issued for the fan app's project.

#### Scenario: Token of another app

- **WHEN** a caller calls with an active access token issued only for the organizer console
- **THEN** the call fails with PermissionDenied and nothing is read or changed

### Requirement: An answer about a token is reused for at most 60 seconds

The fan API MAY reuse an answer that a token is active for at most 60 seconds, and never past the token's expiry. While the sign-in service cannot be asked and no such answer holds, a call that needs a sign-in SHALL fail with Unavailable.

#### Scenario: Calls within a minute

- **WHEN** a caller makes 2 calls with one active token 10 seconds apart and the sign-in service becomes unreachable between them
- **THEN** both calls are handled

#### Scenario: Sign-in service unreachable

- **WHEN** a caller calls with a token not asked about in the last 60 seconds while the sign-in service is unreachable
- **THEN** the call fails with Unavailable and nothing is read or changed

#### Scenario: Expired token

- **WHEN** a token reported active 10 seconds ago has since expired
- **THEN** the call fails with Unauthenticated

### Requirement: Calls open to everyone ignore a refused token

A call the fan API serves without a sign-in SHALL be handled as a call with no sign-in when its token is refused or cannot be checked.

#### Scenario: Refused token on a public call

- **WHEN** a caller reads a public concert with an ID token
- **THEN** the concert is returned as to a guest
