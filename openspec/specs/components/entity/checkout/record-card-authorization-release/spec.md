# components/entity/checkout/record-card-authorization-release Specification

## Purpose
Records that an ended Checkout's card authorization was given back, so it is not released again.

## Requirements

### Requirement: Release recorded once

RecordCardAuthorizationRelease SHALL set the card authorization release time of an Expired or Released Checkout that has a card authorization, and SHALL change nothing when it is already set. It SHALL fail with FailedPrecondition for a Checkout in any other status or without a card authorization, and with NotFound when no Checkout has the id.

#### Scenario: Card authorization given back
- **WHEN** the card authorization of an Expired Checkout is released at 18:16
- **THEN** its card authorization release time is 18:16
