## MODIFIED Requirements

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
