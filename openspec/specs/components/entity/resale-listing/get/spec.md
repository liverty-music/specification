# components/entity/resale-listing/get Specification

## Purpose
Reads one ResaleListing by its id, so a usecase can check its user and status before acting on it.

## Requirements

### Requirement: Get a listing

Get SHALL return the ResaleListing with the given id, with its Checkout when it has one, and SHALL fail with NotFound when no listing has the id.

#### Scenario: Existing listing
- **WHEN** Get is called with the id of a Listed listing
- **THEN** the listing is returned

#### Scenario: Unknown listing
- **WHEN** no listing has the id
- **THEN** Get fails with NotFound
