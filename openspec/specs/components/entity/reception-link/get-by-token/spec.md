# components/entity/reception-link/get-by-token Specification

## Purpose
Finds the ReceptionLink a link URL's token belongs to.

## Requirements

### Requirement: GetByToken returns the link that holds the token

GetByToken SHALL return the ReceptionLink whose token equals the given token, whatever its status, and SHALL fail with NotFound when no link holds it. Comparing tokens SHALL take the same time whatever the given token is.

#### Scenario: Known token

- **WHEN** the token of an Unused link is given
- **THEN** that link is returned

#### Scenario: Unknown token

- **WHEN** no link holds the token
- **THEN** GetByToken fails with NotFound
