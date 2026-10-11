# Spec Delta

## Purpose

Lists Checkouts that need finishing: lapsed holds, card holds still to give back, and commits whose issuance did not complete.

## ADDED Requirements

### Requirement: Lapsed holds, card holds to give back and stalled commits

ListDue SHALL take a time and return, oldest first:
- the Held Checkouts whose hold expired at or before that time;
- the Expired and Released Checkouts that have an authorization reference and no authorization release time;
- the Committed Checkouts committed more than 1 minute before that time.

It SHALL return an empty list when there are none.

#### Scenario: One of each
- **WHEN** at 18:30 one Held Checkout expired at 18:20, one Released Checkout still has its card hold, and one was committed at 18:28 without completing
- **THEN** all three are returned

#### Scenario: Fresh commit
- **WHEN** a Checkout was committed 30 seconds ago
- **THEN** it is not returned

#### Scenario: Card hold already given back
- **WHEN** an Expired Checkout has an authorization release time
- **THEN** it is not returned
