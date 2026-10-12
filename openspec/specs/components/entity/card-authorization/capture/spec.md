# components/entity/card-authorization/capture Specification

## Purpose
Captures an Authorized CardAuthorization, charging the fan's card its amount, exactly once however often and however late it is repeated.

## Requirements

### Requirement: Capture a card authorization once

CardAuthorization.Capture SHALL charge the card the CardAuthorization's amount and make it Captured. The outcome SHALL follow the CardAuthorization's status, not the outcome of an earlier request:
- When it is already Captured, by this call or any earlier one however long ago, it SHALL succeed without charging again.
- When it is Pending or Released, or the card can no longer be charged, it SHALL fail with FailedPrecondition and nothing is charged.
- When the outcome cannot be known yet, because the payment provider cannot be reached or another capture of the same CardAuthorization is still in progress, it SHALL fail with Unavailable.

It SHALL fail with NotFound when no CardAuthorization has the id.

#### Scenario: Card authorization captured
- **WHEN** CardAuthorization.Capture is called for an Authorized card authorization
- **THEN** its amount is charged and it is Captured

#### Scenario: Repeated capture
- **WHEN** CardAuthorization.Capture is called again for the same card authorization
- **THEN** it succeeds and the card is charged only once

#### Scenario: Repeated days later
- **WHEN** CardAuthorization.Capture is called for a card authorization that was captured 2 days earlier
- **THEN** it succeeds without charging again

#### Scenario: No longer capturable
- **WHEN** the card authorization was released or the card was closed
- **THEN** CardAuthorization.Capture fails with FailedPrecondition and nothing is charged

#### Scenario: Capture already in progress
- **WHEN** another capture of the same card authorization has not finished
- **THEN** CardAuthorization.Capture fails with Unavailable

#### Scenario: Unknown id
- **WHEN** no card authorization has the id
- **THEN** CardAuthorization.Capture fails with NotFound
