# Spec Delta

## Purpose

Records the card hold opened for a Checkout; it changes no other attribute.

## ADDED Requirements

### Requirement: Hold recorded once

SetAuthorization SHALL take a Checkout and an authorization reference, and store the reference while the Checkout is Held. When the Checkout already has the same authorization reference, it SHALL change nothing and succeed. It SHALL fail with FailedPrecondition when the Checkout has another authorization reference or is not Held, and with NotFound when no Checkout has the id.

#### Scenario: First authorization
- **WHEN** a Held Checkout without a hold gets a hold reference
- **THEN** the reference is stored and the Checkout's other attributes are unchanged

#### Scenario: Same hold on retry
- **WHEN** the same hold reference is set again
- **THEN** SetAuthorization succeeds and nothing changes

#### Scenario: Another hold
- **WHEN** the Checkout already has a different hold reference
- **THEN** SetAuthorization fails with FailedPrecondition and nothing changes

#### Scenario: Expired checkout
- **WHEN** the Checkout is Expired
- **THEN** SetAuthorization fails with FailedPrecondition
