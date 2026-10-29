# components/entity/checkout/commit Specification

## Purpose
Commits a holding Checkout's tickets against its TicketStock before the card is charged.

## Requirements

### Requirement: Commit a holding checkout

Commit SHALL take a Checkout and a time:
- When the Checkout is holding at that time, Commit SHALL make it Committed with that commit time and report Committed. Its Order's ticket count then counts in its TicketStock's sold count.
- When it is already Committed or Completed, it SHALL change nothing and report Committed.
- Otherwise — Held with its hold lapsed, Expired or Released — it SHALL change nothing and report NotHeld.

Checking and committing SHALL be one indivisible step that succeeds only while the Checkout is still Held and before its hold expiry. A holding Checkout's tickets are already counted against the stock, so committing never oversells. It SHALL fail with NotFound when no Checkout has the id.

#### Scenario: Within the hold
- **WHEN** a holding Checkout for 2 tickets is committed
- **THEN** it is Committed and its TicketStock's sold count grows by 2

#### Scenario: Last tickets committed
- **WHEN** a holding Checkout for the last 2 tickets of a TicketStock of 150 is committed at 20:15
- **THEN** the sold count is 150, the TicketStock is SoldOut and its resale is open

#### Scenario: Hold lapsed
- **WHEN** a Held Checkout expiring at 18:15 is committed at 18:15
- **THEN** nothing changes and Commit reports NotHeld

#### Scenario: Repeated commit
- **WHEN** a Committed Checkout is committed again
- **THEN** nothing changes and Commit reports Committed
