## MODIFIED Requirements

### Requirement: Commit only while holding

Commit SHALL take a Checkout and a time:
- When the Checkout is holding at that time, Commit SHALL make it Committed with that commit time and report Committed. For a Checkout that holds stock, it SHALL also add its count to the TicketType's sold count and, when the sold count then equals the quantity and the TicketType has no resale open time, set the resale open time to that time. A resale Checkout leaves the sold count unchanged; its listings stay held by it.
- When it is already Committed or Completed, it SHALL change nothing and report Committed.
- Otherwise — Held with its hold lapsed, Expired or Released — it SHALL change nothing and report NotHeld.

Checking and committing SHALL be one indivisible step that succeeds only while the Checkout is still Held and before its hold expiry. A holding Checkout's tickets are already counted against the stock, so committing never oversells. It SHALL fail with NotFound when no Checkout has the id.

#### Scenario: Within the hold
- **WHEN** a holding Checkout for 2 tickets is committed
- **THEN** it is Committed and the TicketType's sold count grows by 2

#### Scenario: Last tickets committed
- **WHEN** a holding Checkout for the last 2 tickets of a TicketType of 150 is committed at 20:15
- **THEN** the sold count is 150 and the TicketType's resale open time is 20:15

#### Scenario: Resale checkout committed
- **WHEN** a holding resale Checkout for 1 ticket is committed
- **THEN** it is Committed and the TicketType's sold count does not change

#### Scenario: Hold lapsed
- **WHEN** a Held Checkout expiring at 18:15 is committed at 18:15
- **THEN** nothing changes and Commit reports NotHeld

#### Scenario: Repeated commit
- **WHEN** a Committed Checkout is committed again
- **THEN** nothing changes and Commit reports Committed
