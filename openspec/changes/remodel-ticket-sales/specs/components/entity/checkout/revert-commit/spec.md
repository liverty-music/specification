# Spec Delta

## ADDED Requirements

### Requirement: Revert an uncharged commit

RevertCommit SHALL make a Committed Checkout without a capture time Released and its Order Void, in one indivisible step, keeping its commit time so it stays known that it was committed. Its tickets no longer count in its TicketStock's sold count. It SHALL fail with FailedPrecondition, changing nothing, when the Checkout has a capture time. A Checkout that is not Committed SHALL be left unchanged. It SHALL fail with NotFound when no Checkout has the id.

#### Scenario: Card closed after the commit
- **WHEN** a Committed, uncharged Checkout for 2 committed at 18:10 is reverted
- **THEN** it is Released with commit time 18:10, its Order is Void, and its TicketStock's sold count falls by 2

#### Scenario: Already charged
- **WHEN** a Committed Checkout with a capture time is reverted
- **THEN** RevertCommit fails with FailedPrecondition and nothing changes


## REMOVED Requirements

### Requirement: Revert only an uncharged commit

**Reason**: A Checkout no longer buys resale tickets; official resale is bought through its own lottery, added by the change resell-tickets-by-lottery.
**Migration**: None in this change; resale Checkouts are deleted with the rest of the Organizer sales' data (design "Migration Plan").
