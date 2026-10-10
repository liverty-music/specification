# Spec Delta

## MODIFIED Requirements

### Requirement: Own order only

GetOrder SHALL read the Order with Order.Get and return it when the calling fan is its user. It SHALL fail with NotFound when the Order does not exist and, in the same way, when it belongs to another account, so the existence of other users' Orders is not revealed.

#### Scenario: Own order
- **WHEN** a fan asks for their own Order
- **THEN** the Order is returned

#### Scenario: Another buyer's order
- **WHEN** a fan asks for an Order of another account
- **THEN** GetOrder fails with NotFound

#### Scenario: Unknown order
- **WHEN** the Order does not exist
- **THEN** GetOrder fails with NotFound
