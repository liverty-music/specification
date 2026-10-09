# components/entity/user/delete-identity Specification

## Purpose
User.DeleteIdentity removes a User's sign-in identity, so the person can no longer sign in with it.

## Requirements

### Requirement: DeleteIdentity removes the sign-in identity

DeleteIdentity SHALL remove the sign-in identity the User is linked to. An identity that no longer exists SHALL count as removed, so a repeated call succeeds. When the identity cannot be removed it SHALL fail with Internal and the identity stays.

#### Scenario: Existing identity

- **WHEN** DeleteIdentity runs for a User's identity
- **THEN** that identity can no longer sign in

#### Scenario: Already removed

- **WHEN** the identity no longer exists
- **THEN** DeleteIdentity succeeds
