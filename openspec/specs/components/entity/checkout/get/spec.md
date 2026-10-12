# components/entity/checkout/get Specification

## Purpose
Reads one Checkout by its id, whatever its status.

## Requirements

### Requirement: Get returns the checkout

Get SHALL return the Checkout with the given id, whatever its status, and SHALL fail with NotFound when no Checkout has the id.

#### Scenario: Completed checkout
- **WHEN** a Completed Checkout is read
- **THEN** it is returned with status Completed

#### Scenario: Unknown checkout
- **WHEN** no Checkout has the id
- **THEN** Get fails with NotFound
