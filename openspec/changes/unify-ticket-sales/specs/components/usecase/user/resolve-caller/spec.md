# Spec Delta

## ADDED Requirements

### Requirement: The caller's own User

ResolveCaller SHALL read the caller's User by the sign-in identity (User.GetByExternalID) and return it, failing with NotFound when the identity has no User. A request never names a User id, so a per-user call always acts on the caller's own User.

#### Scenario: Signed-in caller with an account
- **WHEN** a signed-in caller with a User makes a per-user request
- **THEN** ResolveCaller returns the caller's User

#### Scenario: Caller without an account
- **WHEN** the signed-in caller's identity has no User
- **THEN** ResolveCaller fails with NotFound

## REMOVED Requirements

### Requirement: The named User must be the caller
**Reason**: Per-user requests no longer name a User id; the User is taken from the sign-in identity alone, so there is no named id to compare.
**Migration**: Replaced by "The caller's own User". Clients stop sending the User id; a client that kept another account's id after an account switch clears its state instead.
