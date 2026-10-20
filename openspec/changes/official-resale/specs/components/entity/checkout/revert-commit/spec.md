## MODIFIED Requirements

### Requirement: Revert only an uncharged commit

RevertCommit SHALL make a Committed Checkout without a capture time Released, in one indivisible step, keeping its commit time so it stays known that it was committed. For a Checkout that holds stock it SHALL also take its count off the TicketType's sold count, leaving any resale open time as it is; a resale Checkout's listings become free again. It SHALL fail with FailedPrecondition, changing nothing, when the Checkout has a capture time. A Checkout that is not Committed SHALL be left unchanged. It SHALL fail with NotFound when no Checkout has the id.

#### Scenario: Card closed after the commit
- **WHEN** a Committed, uncharged Checkout for 2 committed at 18:10 is reverted
- **THEN** it is Released with commit time 18:10, and the TicketType's sold count falls by 2

#### Scenario: Resale card closed after the commit
- **WHEN** a Committed, uncharged resale Checkout holding 1 listing is reverted before the resale deadline
- **THEN** it is Released, the sold count does not change and the listing is free again

#### Scenario: Already charged
- **WHEN** a Committed Checkout with a capture time is reverted
- **THEN** RevertCommit fails with FailedPrecondition and nothing changes
