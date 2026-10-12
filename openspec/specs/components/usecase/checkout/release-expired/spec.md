# components/usecase/checkout/release-expired Specification

## Purpose
CheckoutUseCase.ReleaseExpired ends Checkouts whose hold lapsed and gives back the card authorizations of every ended Checkout, so the tickets go back on sale and no fan stays authorized for nothing.

## Requirements

### Requirement: Lapsed holds and leftover card authorizations handled within one minute

ReleaseExpired SHALL run every 1 minute over the Checkouts returned by Checkout.ListDue:
- For a Held Checkout, it SHALL call Checkout.Release. A Checkout committed meanwhile is left Committed.
- For an Expired or Released Checkout with a card authorization and no card authorization release time, it SHALL release the card authorization with CardAuthorization.Release and then call Checkout.RecordCardAuthorizationRelease. This includes a Checkout just expired, one replaced when the fan started again, and one whose commit was reverted.

A Checkout whose handling fails SHALL NOT stop the others and is tried again on the next run.

#### Scenario: Fan walked away
- **WHEN** a fan's hold expired at 18:15 after authorizing their card
- **THEN** within 1 minute after the hold expired the Checkout is Expired and its tickets are on sale again, and within 1 more minute the card authorization is released

#### Scenario: Count changed after authorizing
- **WHEN** a fan authorized their card for 2 tickets and then started again for 3
- **THEN** the card authorization of the 2-ticket Checkout is released within 1 minute

#### Scenario: Committed at the last moment
- **WHEN** a Checkout is committed just before ReleaseExpired handles it
- **THEN** it stays Committed and its card authorization is not released

#### Scenario: Release fails
- **WHEN** releasing one card authorization fails with Unavailable
- **THEN** the other Checkouts are still handled and the failed release is tried again 1 minute later

### Requirement: A captured card authorization on an ended checkout is reported

When CardAuthorization.Release fails with FailedPrecondition because the card authorization of an Expired or Released Checkout was captured, ReleaseExpired SHALL report that Checkout, with its id and its card authorization's id, as needing an operator on every run until it is resolved, and SHALL go on with the others.

#### Scenario: Money taken on an ended checkout
- **WHEN** the card authorization of a Released Checkout turns out to have been captured
- **THEN** the Checkout is reported as needing an operator on every run
