# components/entity/checkout/get-by-card-authorization-id Specification

## Purpose
Finds the Checkout a card authorization was opened for, so a charge reported by the payment provider can be traced back to it.

## Requirements

### Requirement: The checkout of a card authorization

GetByCardAuthorizationID SHALL return the Checkout whose Order's card authorization has the given id, and SHALL fail with NotFound when there is none.

#### Scenario: Charged checkout
- **WHEN** the card authorization of a Checkout's Order is looked up
- **THEN** that Checkout is returned

#### Scenario: Unknown card authorization
- **WHEN** no Checkout's Order has a card authorization with the id
- **THEN** GetByCardAuthorizationID fails with NotFound
