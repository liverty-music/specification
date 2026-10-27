## Purpose

Returns the User registered with a given email address, so an admin can find the account a fan asks to have removed by the address the request came from.

## ADDED Requirements

### Requirement: GetByEmail returns the user by address

GetByEmail SHALL call User.GetByEmail with the given address and return the User. A missing User SHALL fail with NotFound, an empty address with InvalidArgument, and any other failure to read SHALL be returned with its own code.

#### Scenario: Registered address

- **WHEN** GetByEmail is called with `Fan@Example.com` and a User's email is `fan@example.com`
- **THEN** it returns that User

#### Scenario: Unregistered address

- **WHEN** no User has the given address
- **THEN** GetByEmail fails with NotFound
