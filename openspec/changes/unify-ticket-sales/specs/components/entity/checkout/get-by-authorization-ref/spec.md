# Spec Delta

## Purpose

Finds the Checkout a card hold was opened for, so a charge reported by the payment provider can be traced back to it.

## ADDED Requirements

### Requirement: The checkout of a card hold

GetByAuthorizationRef SHALL return the Checkout whose authorization reference is the given one, and SHALL fail with NotFound when there is none.

#### Scenario: Charged checkout
- **WHEN** the card hold of a Checkout is looked up
- **THEN** that Checkout is returned

#### Scenario: Unknown hold
- **WHEN** no Checkout has the authorization reference
- **THEN** GetByAuthorizationRef fails with NotFound
