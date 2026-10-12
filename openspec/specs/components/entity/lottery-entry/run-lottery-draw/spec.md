# components/entity/lottery-entry/run-lottery-draw Specification

## Purpose
Computes a lottery draw: orders the given entries at random and admits whole entries that fit a ticket quantity, returning the winners and the losers in draw order.

## Requirements

### Requirement: Random order with greedy whole-entry fit

RunLotteryDraw SHALL put the entries in a uniformly random order, numbering each with its draw position from 0, then walk that order once and admit each entry whose ticket count is greater than 0 and fits the remaining quantity, deducting its whole count. An entry that does not fit SHALL be placed among the losers and the walk SHALL continue, so a later, smaller entry can still fill the remaining quantity. Every entry SHALL appear exactly once, either as a winner or as a loser.

#### Scenario: Demand above quantity

- **WHEN** entries totalling more tickets than the quantity are drawn
- **THEN** the tickets won never exceed the quantity and every entry is either a winner or a loser

#### Scenario: Companion group is all-or-nothing

- **WHEN** an entry for 3 tickets is admitted
- **THEN** it wins all 3 tickets, never fewer

#### Scenario: A smaller entry fills the gap

- **WHEN** 1 ticket remains, an entry for 2 tickets comes next in the order and an entry for 1 ticket follows it
- **THEN** the 2-ticket entry loses and the 1-ticket entry wins

#### Scenario: Demand at or below quantity

- **WHEN** the total requested tickets do not exceed the quantity
- **THEN** every entry wins and there are no losers

#### Scenario: No entries

- **WHEN** no entry is given
- **THEN** there are no winners and no losers

#### Scenario: Non-positive request

- **WHEN** an entry requests 0 tickets
- **THEN** it loses and deducts nothing from the quantity

### Requirement: Losers in draw order

The losers SHALL be the entries that were not admitted, listed in ascending draw position.

#### Scenario: Order of the losers

- **WHEN** the entries at draw positions 5, 2 and 7 are not admitted
- **THEN** the losers are listed as 2, 5, 7
