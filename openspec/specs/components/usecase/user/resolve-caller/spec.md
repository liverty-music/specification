# components/usecase/user/resolve-caller Specification

## Purpose
UserUseCase.ResolveCaller turns a signed-in identity into its User and admits a per-user request only when the User it names is that User, so no fan can read or change another fan's account.

## Requirements

### Requirement: The named User must be the caller

ResolveCaller SHALL read the caller's User by the sign-in identity (User.GetByExternalID) and fail with NotFound when the identity has no User. It SHALL then fail with InvalidArgument when the request names no User id, and with PermissionDenied when the named id is not the caller's User's id, before any other read or any change, so the failure reveals nothing about the named User. Otherwise it SHALL return the caller's User.

#### Scenario: Own account

- **WHEN** a signed-in caller names their own User id
- **THEN** ResolveCaller returns the caller's User

#### Scenario: Another user's account

- **WHEN** a signed-in caller names a different User's id
- **THEN** ResolveCaller fails with PermissionDenied

#### Scenario: Missing user id

- **WHEN** a signed-in caller with a User names no User id
- **THEN** ResolveCaller fails with InvalidArgument

#### Scenario: Caller has no account

- **WHEN** the signed-in caller's identity has no User
- **THEN** ResolveCaller fails with NotFound
