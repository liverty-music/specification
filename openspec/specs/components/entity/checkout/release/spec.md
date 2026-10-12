# components/entity/checkout/release Specification

## Purpose
Ends a Held Checkout whose hold has lapsed, so its tickets go back on sale.

## Requirements

### Requirement: Release ends only a lapsed Held checkout

Release SHALL take a Checkout and a time, and make it Expired only when it is still Held and its hold expired at or before that time. Checking and changing SHALL be one indivisible step, so a Checkout committed meanwhile is left Committed. A Checkout in any other status, or still holding, SHALL be left unchanged. Release SHALL report whether it changed the Checkout, and SHALL fail with NotFound when no Checkout has the id.

#### Scenario: Hold lapsed
- **WHEN** a Held Checkout expiring at 18:15 is released at 18:16
- **THEN** it is Expired and Release reports a change

#### Scenario: Still holding
- **WHEN** a Held Checkout expiring at 18:15 is released at 18:14
- **THEN** nothing changes

#### Scenario: Committed just before the sweep
- **WHEN** a Checkout was committed at 18:14 and is released at 18:16
- **THEN** it stays Committed and Release reports no change

#### Scenario: Paid checkout
- **WHEN** a Completed Checkout is released
- **THEN** nothing changes
