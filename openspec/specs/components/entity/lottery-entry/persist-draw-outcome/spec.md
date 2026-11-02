# components/entity/lottery-entry/persist-draw-outcome Specification

## Purpose
Records the outcome of one TicketSale's draw: each winner Won and each loser Lost, every one with its draw position, and the sale as drawn.

## Requirements

### Requirement: Draw outcome is recorded together

PersistDrawOutcome SHALL take a sale and, for each TicketStock of the sale's events, the stock's Entered entries of the sale in their draw order. It SHALL walk each stock's entries in that order once and admit each entry whose ticket count fits the stock's remaining count at the time it records, deducting its whole count; an entry that does not fit SHALL be Lost and the walk SHALL continue. It SHALL set every admitted entry Won and every other given entry Lost with the lost reason "not drawn", each with its draw position, and make every Lost entry's Order Void, all together or not at all. A given entry that is no longer Entered SHALL be left unchanged, so recording the same draw again leaves the first record, including any entry made Lost since. Once no entry of the closed sale is Entered, the sale is drawn (components/entity/ticket-sale "Drawn lottery").

#### Scenario: Outcome recorded
- **WHEN** PersistDrawOutcome is called with the ordered entries of two TicketStocks of a sale
- **THEN** the admitted entries are Won, the others are Lost with the lost reason "not drawn" and their Orders Void, each carries its draw position, and the sale is drawn

#### Scenario: Failure leaves nothing recorded
- **WHEN** recording any part of the outcome fails
- **THEN** no entry state, lost reason, Order status or draw position is changed

#### Scenario: Empty draw
- **WHEN** PersistDrawOutcome is called with no entries
- **THEN** no entry changes

#### Scenario: Recorded again
- **WHEN** PersistDrawOutcome is called again for a sale whose outcome is recorded, after one of its winners was made Lost
- **THEN** it succeeds and no entry changes

#### Scenario: Tickets taken since the order was fixed
- **WHEN** a stock had 4 remaining tickets when its entries for 2, 2 and 3 tickets were ordered, and 2 of its tickets were taken before the outcome is recorded
- **THEN** only the first 2-ticket entry in draw order is Won, and the stock's sold count never exceeds its quantity

### Requirement: Each drawn entry is announced with the outcome

PersistDrawOutcome SHALL announce each entry it sets Won or Lost, as it is after the draw, together with the outcome: the outcome and its announcements are stored together or not at all. An entry it leaves unchanged SHALL NOT be announced. When an announcement cannot be recorded, PersistDrawOutcome SHALL fail with Unavailable and record nothing. Each announcement is what product analytics records as one "lottery result" signal for the fan of the entry's Order.

#### Scenario: Two entries, one place
- **WHEN** PersistDrawOutcome records one entry Won and one entry Lost
- **THEN** two lottery results are announced, one per entry

#### Scenario: Recorded again announces nothing
- **WHEN** PersistDrawOutcome is called again with an outcome already recorded
- **THEN** nothing is announced

#### Scenario: Announcement cannot be recorded
- **WHEN** an entry's announcement cannot be recorded
- **THEN** PersistDrawOutcome fails with Unavailable and no entry, lost reason or Order status is changed
