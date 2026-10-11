# User.GetByProviderUserID

## Purpose

Returns the User linked to a given identity at the identity provider, including its Home when one is set.

## Requirements

### Requirement: GetByProviderUserID returns the user or NotFound

GetByProviderUserID SHALL return the User whose provider user ID equals the given value, carrying its Home, centroid included, when one is set. It SHALL fail with NotFound when no User has that provider user ID, and with InvalidArgument when the value is empty. Any other failure to read SHALL be returned with its own code, not as NotFound.

#### Scenario: Registered identity

- **WHEN** GetByProviderUserID runs for the provider user ID of a stored User
- **THEN** it returns that User with its Home, if any

#### Scenario: Unregistered identity

- **WHEN** no User has the given provider user ID
- **THEN** GetByProviderUserID fails with NotFound

#### Scenario: Empty provider user ID

- **WHEN** the provider user ID is empty
- **THEN** GetByProviderUserID fails with InvalidArgument
