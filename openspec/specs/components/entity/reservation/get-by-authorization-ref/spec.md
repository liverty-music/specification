# components/entity/reservation/get-by-authorization-ref Specification

## Purpose
Finds the checkout a card hold was opened for, so a charge reported by the payment provider can be traced back to it.

## Requirements

### Requirement: The checkout of a card hold

GetByAuthorizationRef SHALL return the Reservation whose authorization reference is the given one, and SHALL fail with NotFound when there is none.

#### Scenario: Charged checkout

- **WHEN** the card hold of a Reservation is looked up
- **THEN** that Reservation is returned

#### Scenario: Unknown hold

- **WHEN** no Reservation has the authorization reference
- **THEN** GetByAuthorizationRef fails with NotFound
