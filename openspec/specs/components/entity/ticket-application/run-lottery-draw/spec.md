# TicketApplication.RunLotteryDraw

## Purpose

Computes a lottery draw: orders the given applications at random and admits whole applications that fit a ticket capacity, returning the winners and the ordered waitlist.

## Requirements

### Requirement: Random order with greedy whole-application fit

RunLotteryDraw SHALL put the applications in a uniformly random order, numbering each with its draw position from 0, then walk that order once and admit each application whose requested ticket count is greater than 0 and fits the remaining capacity, deducting its whole count. An application that does not fit SHALL be placed on the waitlist and the walk SHALL continue, so a later, smaller application can still fill the remaining capacity. Every application SHALL appear exactly once, either as a winner or on the waitlist.

#### Scenario: Demand above capacity

- **WHEN** applications totalling more tickets than the capacity are drawn
- **THEN** the tickets won never exceed the capacity and every application is either a winner or waitlisted

#### Scenario: Companion group is all-or-nothing

- **WHEN** an application for 3 tickets is admitted
- **THEN** it wins all 3 tickets, never fewer

#### Scenario: A smaller application fills the gap

- **WHEN** 1 ticket remains, an application for 2 tickets comes next in the order and an application for 1 ticket follows it
- **THEN** the 2-ticket application is waitlisted and the 1-ticket application wins

#### Scenario: Demand at or below capacity

- **WHEN** the total requested tickets do not exceed the capacity
- **THEN** every application wins and the waitlist is empty

#### Scenario: No applications

- **WHEN** no application is given
- **THEN** there are no winners and the waitlist is empty

#### Scenario: Non-positive request

- **WHEN** an application requests 0 tickets
- **THEN** it is waitlisted and deducts nothing from the capacity

### Requirement: Waitlist in draw order

The waitlist SHALL list the applications that were not admitted in ascending draw position.

#### Scenario: Waitlist order

- **WHEN** the applications at draw positions 5, 2 and 7 are not admitted
- **THEN** the waitlist lists them as 2, 5, 7
