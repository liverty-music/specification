# components/entity/checkout/revert-commit Specification

## Purpose
Gives a Committed Checkout's tickets back to its TicketType when its card can no longer be charged.

## Requirements

### Requirement: Revert an uncharged commit

RevertCommit SHALL make a Committed Checkout without a capture time Released and its Order Void, in one indivisible step, keeping its commit time so it stays known that it was committed. Its tickets no longer count in its TicketStock's sold count. It SHALL fail with FailedPrecondition, changing nothing, when the Checkout has a capture time. A Checkout that is not Committed SHALL be left unchanged. It SHALL fail with NotFound when no Checkout has the id.

#### Scenario: Card closed after the commit
- **WHEN** a Committed, uncharged Checkout for 2 committed at 18:10 is reverted
- **THEN** it is Released with commit time 18:10, its Order is Void, and its TicketStock's sold count falls by 2

#### Scenario: Already charged
- **WHEN** a Committed Checkout with a capture time is reverted
- **THEN** RevertCommit fails with FailedPrecondition and nothing changes
