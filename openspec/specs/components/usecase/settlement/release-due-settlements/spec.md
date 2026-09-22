# Release Due Settlements

## Purpose

This capability settles ticket money **out** to the Organizer. Buyer funds captured
by ④ sit on the **platform balance** (Stripe **separate charges & transfers**); after
the event this capability `Transfer`s the Organizer's net share (the platform retains
its fee) to the Organizer's **Stripe connected account**, and executes refunds/dispute
clawbacks — all under the 収納代行 scheme with the Organizer as seller-of-record.

## Requirements

### Requirement: Payout release gated on event occurrence plus dispute buffer

A payout Transfer SHALL be released only after **the event's `start_time` (of its
currently-scheduled date) has passed AND a dispute-safety window has elapsed**. On a
**postponement (延期)** the release clock SHALL **reset to the new date** (never release
on a stale original date). This counter-performance gate is load-bearing for the 収納代行
characterization (the gate matters, not a bright-line N-day).

#### Scenario: No release before event plus buffer

- **WHEN** the event's current start_time has not passed, or the dispute buffer has not elapsed
- **THEN** the Organizer payout for that sale is not released

#### Scenario: Postponement resets the release clock

- **WHEN** an event is postponed to a later date
- **THEN** the payout release is re-gated on the new date (the original date does not trigger release)
