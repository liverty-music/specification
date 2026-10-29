# Spec Delta

## MODIFIED Requirements

### Requirement: Lapsed holds and leftover card authorizations handled within one minute

ReleaseExpired SHALL run every 1 minute over the Checkouts returned by Checkout.ListDue:
- For a Held Checkout, it SHALL call Checkout.Release, which makes the Checkout Expired and its Order Void. A Checkout committed meanwhile is left Committed.
- For an Expired or Released Checkout whose Order has a card authorization and that has no card authorization release time, it SHALL release the card authorization with CardAuthorization.Release and then call Checkout.RecordCardAuthorizationRelease. This includes a Checkout just expired, one replaced when the fan started again, and one whose commit was reverted.

A Checkout whose handling fails SHALL NOT stop the others and is tried again on the next run.

#### Scenario: Fan walked away
- **WHEN** a fan's hold expired at 18:15 after authorizing their card
- **THEN** within 1 minute after the hold expired the Checkout is Expired, its Order is Void and its tickets are on sale again, and within 1 more minute the card authorization is released

#### Scenario: Count changed after authorizing
- **WHEN** a fan authorized their card for 2 tickets and then started again for 3
- **THEN** the card authorization of the 2-ticket Checkout's Order is released within 1 minute

#### Scenario: Committed at the last moment
- **WHEN** a Checkout is committed just before ReleaseExpired handles it
- **THEN** it stays Committed, its Order stays Pending and its card authorization is not released

#### Scenario: Release fails
- **WHEN** releasing one card authorization fails with Unavailable
- **THEN** the other Checkouts are still handled and the failed release is tried again 1 minute later

### Requirement: Each expired checkout is reported

When ReleaseExpired ends a Checkout because its hold lapsed, it SHALL send a "checkout expired" signal for product analytics for the Checkout's Order's fan, carrying the Checkout, its Order's TicketStock, the ticket count and the hold's expiry as the time it happened. A Checkout ended for another reason SHALL NOT send this signal. A failure to send it SHALL NOT change the release.

#### Scenario: Hold lapsed
- **WHEN** a Checkout's hold lapses before the fan pays
- **THEN** one checkout-expired signal is sent for that fan
