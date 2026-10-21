## Purpose

Records that the user of a Sold ResaleListing was refunded, with the payment provider's refund ID.

## ADDED Requirements

### Requirement: Refund recorded once

RecordRefund SHALL take a ResaleListing, a provider refund ID and a time, and set the listing's provider refund ID and refund time when it is Sold and has no refund time. When it already has a refund time, it SHALL change nothing. It SHALL fail with FailedPrecondition, changing nothing, when the listing is not Sold, and with NotFound when no listing has the id.

#### Scenario: Refund recorded
- **WHEN** RecordRefund is called for a Sold listing without a refund
- **THEN** its provider refund ID and refund time are set

#### Scenario: Recorded twice
- **WHEN** RecordRefund is called again for the same listing
- **THEN** the first refund ID and time are kept

#### Scenario: Listing not sold
- **WHEN** RecordRefund is called for a Listed listing
- **THEN** it fails with FailedPrecondition
