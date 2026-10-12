# components/usecase/user/resolve-caller Specification

## Purpose
UserUseCase.ResolveCaller turns a signed-in identity into its User and admits a per-user request only when the User it names is that User, so no fan can read or change another fan's account.

## Requirements

### Requirement: The caller's own User

ResolveCaller SHALL read the caller's User by the sign-in identity (User.GetByProviderUserID) and return it, failing with NotFound when the identity has no User. A request never names a User id, so a per-user call always acts on the caller's own User.

#### Scenario: Signed-in caller with an account
- **WHEN** a signed-in caller with a User makes a per-user request
- **THEN** ResolveCaller returns the caller's User

#### Scenario: Caller without an account
- **WHEN** the signed-in caller's identity has no User
- **THEN** ResolveCaller fails with NotFound
