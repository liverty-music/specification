# components/entity/checkout/revert-commit Specification

## Purpose
Gives a Committed Checkout's tickets back to its TicketStock when its card can no longer be charged.

## Requirements

### Requirement: Revert an uncharged commit

RevertCommit SHALL make a Committed Checkout without a capture time Released and its Order Void, in one indivisible step, keeping its commit time so it stays known that it was committed. Its tickets no longer count in its TicketStock's sold count. It SHALL fail with FailedPrecondition, changing nothing, when the Checkout has a capture time. A Checkout that is not Committed SHALL be left unchanged. It SHALL fail with NotFound when no Checkout has the id.

#### Scenario: Card closed after the commit
- **WHEN** a Committed, uncharged Checkout for 2 committed at 18:10 is reverted
- **THEN** it is Released with commit time 18:10, its Order is Void, and its TicketStock's sold count falls by 2

#### Scenario: Already charged
- **WHEN** a Committed Checkout with a capture time is reverted
- **THEN** RevertCommit fails with FailedPrecondition and nothing changes

### Requirement: A reverted commit is announced with the change

When RevertCommit makes a Checkout Released, it SHALL announce it as released, carrying the Checkout as it is after the change, together with the change: both are stored or neither is. When it changes nothing it SHALL announce nothing. When the announcement cannot be recorded, RevertCommit SHALL fail with Unavailable and change nothing.

#### Scenario: Commit reverted
- **WHEN** RevertCommit makes a Committed Checkout without a capture time Released
- **THEN** one checkout release is announced, carrying the Checkout as Released

#### Scenario: Announcement cannot be recorded
- **WHEN** the announcement cannot be recorded
- **THEN** RevertCommit fails with Unavailable and the Checkout stays Committed
