# components/entity/order/list-by-buyer Specification

## Purpose
Order.ListByBuyer returns every Order a User bought, in any status.

## Requirements

### Requirement: ListByBuyer returns the User's Orders

ListByBuyer SHALL return every Order whose buyer is the given User, whatever its status, and SHALL return an empty list when the User bought none.

#### Scenario: Paid and refunded orders

- **WHEN** the User has one Paid and one Refunded Order
- **THEN** both are returned

#### Scenario: No orders

- **WHEN** the User bought nothing
- **THEN** an empty list is returned
