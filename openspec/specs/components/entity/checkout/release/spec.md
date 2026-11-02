# components/entity/checkout/release Specification

## Purpose
Ends a Held Checkout whose hold has lapsed, so its tickets go back on sale.

## Requirements

### Requirement: Release ends only a lapsed Held checkout

Release SHALL take a Checkout and a time, and make it Expired and its Order Void only when it is still Held and its hold expired at or before that time. Checking and changing SHALL be one indivisible step, so a Checkout committed meanwhile is left Committed. A Checkout in any other status, or still holding, SHALL be left unchanged. Release SHALL report whether it changed the Checkout, and SHALL fail with NotFound when no Checkout has the id.

#### Scenario: Hold lapsed
- **WHEN** a Held Checkout expiring at 18:15 is released at 18:16
- **THEN** it is Expired, its Order is Void and Release reports a change

#### Scenario: Still holding
- **WHEN** a Held Checkout expiring at 18:15 is released at 18:14
- **THEN** nothing changes

#### Scenario: Committed just before the sweep
- **WHEN** a Checkout was committed at 18:14 and is released at 18:16
- **THEN** it stays Committed, its Order stays Pending and Release reports no change

#### Scenario: Paid checkout
- **WHEN** a Completed Checkout is released
- **THEN** nothing changes

### Requirement: An expired Checkout is announced with the change

When Release makes a Checkout Expired and its Order Void, it SHALL announce the Checkout as expired, carrying it in status Expired, together with the change: both are stored or neither is. When Release changes nothing, it SHALL announce nothing. When the announcement cannot be recorded, Release SHALL fail with Unavailable, and the Checkout SHALL stay Held and its Order Pending.

#### Scenario: Hold lapsed

- **WHEN** a Held Checkout expiring at 18:15 is released at 18:16
- **THEN** one checkout expiry is announced, carrying the Checkout as Expired

#### Scenario: Nothing to release

- **WHEN** Release is called for a Checkout that is Committed, Completed, already Expired or still holding
- **THEN** nothing is announced

#### Scenario: Announcement cannot be recorded

- **WHEN** a Held Checkout whose hold lapsed is released and the announcement cannot be recorded
- **THEN** Release fails with Unavailable, the Checkout stays Held and its Order stays Pending
