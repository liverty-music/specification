# Spec Delta

## Purpose

Computes a lottery draw: orders the given entries at random and admits whole entries that fit a ticket capacity, returning the winners and the ordered waitlist.

## ADDED Requirements

### Requirement: Random order with greedy whole-entry fit

RunLotteryDraw SHALL put the entries in a uniformly random order, numbering each with its draw position from 0, then walk that order once and admit each entry whose requested ticket count is greater than 0 and fits the remaining capacity, deducting its whole count. An entry that does not fit SHALL be placed on the waitlist and the walk SHALL continue, so a later, smaller entry can still fill the remaining capacity. Every entry SHALL appear exactly once, either as a winner or on the waitlist.

#### Scenario: Demand above capacity

- **WHEN** entries totalling more tickets than the capacity are drawn
- **THEN** the tickets won never exceed the capacity and every entry is either a winner or waitlisted

#### Scenario: Companion group is all-or-nothing

- **WHEN** an entry for 3 tickets is admitted
- **THEN** it wins all 3 tickets, never fewer

#### Scenario: A smaller entry fills the gap

- **WHEN** 1 ticket remains, an entry for 2 tickets comes next in the order and an entry for 1 ticket follows it
- **THEN** the 2-ticket entry is waitlisted and the 1-ticket entry wins

#### Scenario: Demand at or below capacity

- **WHEN** the total requested tickets do not exceed the capacity
- **THEN** every entry wins and the waitlist is empty

#### Scenario: No entries

- **WHEN** no entry is given
- **THEN** there are no winners and the waitlist is empty

#### Scenario: Non-positive request

- **WHEN** an entry requests 0 tickets
- **THEN** it is waitlisted and deducts nothing from the capacity

### Requirement: Waitlist in draw order

The waitlist SHALL list the entries that were not admitted in ascending draw position.

#### Scenario: Waitlist order

- **WHEN** the entries at draw positions 5, 2 and 7 are not admitted
- **THEN** the waitlist lists them as 2, 5, 7
