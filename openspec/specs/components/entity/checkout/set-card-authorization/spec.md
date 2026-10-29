# components/entity/checkout/set-card-authorization Specification

## Purpose
Records the card authorization opened for a Checkout; it changes no other attribute.

## Requirements

### Requirement: Card authorization recorded once

SetCardAuthorization SHALL take a Checkout and a CardAuthorization, and store it as the card authorization of the Checkout's Order while the Checkout is Held. When the Order already has the same card authorization, it SHALL change nothing and succeed. It SHALL fail with FailedPrecondition when the Order has another card authorization or the Checkout is not Held, and with NotFound when no Checkout has the id.

#### Scenario: First card authorization
- **WHEN** a Held Checkout whose Order has no card authorization gets one
- **THEN** the card authorization is stored on the Order and the other attributes are unchanged

#### Scenario: Same card authorization on retry
- **WHEN** the same card authorization is set again
- **THEN** SetCardAuthorization succeeds and nothing changes

#### Scenario: Another card authorization
- **WHEN** the Order already has a different card authorization
- **THEN** SetCardAuthorization fails with FailedPrecondition and nothing changes

#### Scenario: Expired checkout
- **WHEN** the Checkout is Expired
- **THEN** SetCardAuthorization fails with FailedPrecondition
