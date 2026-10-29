# components/entity/order/list-by-user Specification

## Purpose
Order.ListByUser returns every Order a User bought, in any status.

## Requirements

### Requirement: ListByUser returns the User's Orders

ListByUser SHALL return every Paid or Refunded Order whose user is the given User, and SHALL return an empty list when the User bought none. Pending and Void Orders SHALL NOT be returned.

#### Scenario: Paid and refunded orders
- **WHEN** the User has one Paid and one Refunded Order
- **THEN** both are returned

#### Scenario: Applications not bought
- **WHEN** the User has one Pending Order of an Entered LotteryEntry and one Void Order of an expired Checkout
- **THEN** neither is returned

#### Scenario: No orders
- **WHEN** the User bought nothing
- **THEN** an empty list is returned
