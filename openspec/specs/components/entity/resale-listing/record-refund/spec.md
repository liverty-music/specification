# components/entity/resale-listing/record-refund Specification

## Purpose
Records that the user of a Sold ResaleListing was refunded, with the payment provider's refund ID.

## Requirements

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

### Requirement: A recorded refund is announced with it

When RecordRefund sets the refund, it SHALL announce the ResaleListing as refunded together with the refund: both are stored or neither is. When the listing already has a refund time, RecordRefund SHALL announce nothing. When the announcement cannot be recorded, RecordRefund SHALL fail with Unavailable and set nothing.

#### Scenario: Refund announced
- **WHEN** RecordRefund sets the refund of a Sold listing
- **THEN** the listing is announced as refunded once

#### Scenario: Recorded twice
- **WHEN** RecordRefund is called again for a listing that has a refund time
- **THEN** nothing is announced

#### Scenario: Announcement cannot be recorded
- **WHEN** the refund announcement cannot be recorded
- **THEN** RecordRefund fails with Unavailable and the listing has no refund time
