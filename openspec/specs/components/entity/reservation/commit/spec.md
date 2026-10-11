# components/entity/reservation/commit Specification

## Purpose
Commits a holding Reservation's tickets against its TicketSale's stock before the card is charged.

## Requirements

### Requirement: Commit only while holding

Commit SHALL take a Reservation and a time:
- When the Reservation is holding at that time, Commit SHALL make it Committed with that committed time, add its count to the sale's sold count and report Committed.
- When it is already Committed or Completed, it SHALL change nothing and report Committed.
- Otherwise — Held with its hold lapsed, Expired or Released — it SHALL change nothing and report NotHeld.

Checking and committing SHALL be one indivisible step that succeeds only while the Reservation is still Held and before its hold expiry. A holding Reservation's tickets are already counted against the stock, so committing never oversells. It SHALL fail with NotFound when no Reservation has the id.

#### Scenario: Within the hold

- **WHEN** a holding Reservation for 2 tickets is committed
- **THEN** it is Committed and the sale's sold count grows by 2

#### Scenario: Hold lapsed

- **WHEN** a Held Reservation expiring at 18:15 is committed at 18:15
- **THEN** nothing changes and Commit reports NotHeld

#### Scenario: Repeated commit

- **WHEN** a Committed Reservation is committed again
- **THEN** nothing changes and Commit reports Committed
