## Purpose

Returns the User whose email address matches a given address, so a person who cannot sign in can be matched to their account by the address they type.

## ADDED Requirements

### Requirement: GetByEmail returns the user or NotFound

GetByEmail SHALL return the User whose email equals the given address when letter case is ignored. It SHALL fail with NotFound when no User has that address, and with InvalidArgument when the address is empty. Any other failure to read SHALL be returned with its own code, not as NotFound.

#### Scenario: Registered address

- **WHEN** GetByEmail runs for `fan@example.com` and a User's email is `fan@example.com`
- **THEN** it returns that User

#### Scenario: Different letter case

- **WHEN** GetByEmail runs for `Fan@Example.com` and a User's email is `fan@example.com`
- **THEN** it returns that User

#### Scenario: Unregistered address

- **WHEN** no User has the given address
- **THEN** GetByEmail fails with NotFound

#### Scenario: Empty address

- **WHEN** the address is empty
- **THEN** GetByEmail fails with InvalidArgument
