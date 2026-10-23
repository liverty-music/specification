# components/adapter/fan/api/rpc/passkey Specification

## Purpose
The fan-facing passkey service boundary: a signed-in fan reads only their own recorded passkeys, and the boundary resolves the caller before PasskeyUseCase runs.

## Requirements

### Requirement: Listing passkeys is always for the caller

List SHALL return the recorded passkeys of the signed-in caller, resolved to their stored User (User.GetByProviderUserID), by calling PasskeyUseCase.List; the request names no fan. Each returned passkey SHALL carry its provider passkey id, its provider name when it has one, and its create time. List SHALL fail with Unauthenticated when the caller is not signed in, and with NotFound when the caller has no account.

#### Scenario: Fan lists their passkeys

- **WHEN** a signed-in fan calls List
- **THEN** PasskeyUseCase.List runs for that fan and their recorded passkeys are returned

#### Scenario: Not signed in

- **WHEN** the caller is not authenticated
- **THEN** List fails with Unauthenticated

#### Scenario: No account

- **WHEN** a signed-in caller has no User
- **THEN** List fails with NotFound
