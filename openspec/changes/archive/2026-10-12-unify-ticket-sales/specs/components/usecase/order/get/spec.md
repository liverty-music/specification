# Spec Delta

## ADDED Requirements

### Requirement: Only the fan's own order

Get SHALL read the Order with Order.Get and return it when the calling fan is its user. It SHALL fail with NotFound when the Order does not exist and, in the same way, when it belongs to another account, so the existence of other users' Orders is not revealed.

#### Scenario: Own order
- **WHEN** a fan asks for their own Order
- **THEN** the Order is returned

#### Scenario: Another user's order
- **WHEN** a fan asks for an Order of another account
- **THEN** Get fails with NotFound

#### Scenario: Unknown order
- **WHEN** the Order does not exist
- **THEN** Get fails with NotFound

## REMOVED Requirements

### Requirement: Own order only
**Reason**: An Order belongs to its user; "buyer" is not an entity (design D9), so the scenario "Another buyer's order" is renamed "Another user's order". A MODIFIED block cannot drop a scenario, so the requirement is replaced.
**Migration**: The same rule continues as "Only the fan's own order" above.
