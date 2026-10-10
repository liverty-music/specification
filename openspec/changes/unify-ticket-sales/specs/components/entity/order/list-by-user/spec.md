# Spec Delta

## Purpose

Order.ListByUser returns every Order a User bought, in any status.

## ADDED Requirements

### Requirement: ListByUser returns the User's Orders

ListByUser SHALL return every Order whose user is the given User, whatever its status, and SHALL return an empty list when the User bought none.

#### Scenario: Paid and refunded orders
- **WHEN** the User has one Paid and one Refunded Order
- **THEN** both are returned

#### Scenario: No orders
- **WHEN** the User bought nothing
- **THEN** an empty list is returned
