## Purpose

LotteryEntryUseCase.Draw draws one closed Lottery TicketSale and records who won and who lost, before any card is charged or released.

## ADDED Requirements

### Requirement: Draw a sale without charging

Draw SHALL take a TicketSale. It SHALL read the sale and the events it names with TicketSale.Get, failing with NotFound when it does not exist. For each TicketStock of those events, from TicketStock.ListByEvent, it SHALL take the sale's Entered entries for that stock from LotteryEntry.ListEnteredByTicketSaleAndTicketStock and put them in an unpredictable random order, numbering each with its draw position. It SHALL then record the outcome of every stock with LotteryEntry.PersistDrawOutcome, which admits the entries in that order against each stock's remaining tickets: the admitted entries Won and every other Entered entry Lost with its Order Void, each with its draw position. When the sale has no Entered entry, it SHALL record nothing: the closed sale is already drawn. Draw SHALL NOT capture or release any card authorization and SHALL NOT make an Order Paid or create a Ticket; no loser is promoted (no 繰上げ, promotion of a loser). Draw announces nothing itself: LotteryEntry.PersistDrawOutcome announces each entry it records, together with the outcome.

#### Scenario: Winners and losers recorded
- **WHEN** a closed sale's stock with 4 remaining tickets has Entered entries for 2, 2 and 3 tickets and the random order puts the two 2-ticket entries first
- **THEN** the two 2-ticket entries are Won, the 3-ticket entry is Lost and its Order is Void, no card is charged or released by the draw, and the sale is drawn

#### Scenario: Each stock is drawn against its own remaining tickets
- **WHEN** a sale's event has an S席 stock with 100 remaining and 80 requested and an A席 stock with 4 remaining and 12 requested
- **THEN** every S席 entry is Won, and the A席 Won entries hold at most 4 tickets

#### Scenario: Losers in draw order
- **WHEN** the draw completes with Lost entries
- **THEN** each Lost entry carries its draw position within its stock, so the losers can be read in draw order

#### Scenario: No entries
- **WHEN** the sale has no Entered entry
- **THEN** the sale is drawn and no entry changes

### Requirement: A stopped draw resumes with the same order

The random order of a draw SHALL be computed once. When Draw stops and runs again for the same sale, it SHALL record with the order it computed before, never a new one.

#### Scenario: Stopped before the outcome was recorded
- **WHEN** Draw stops after ordering the entries of a sale's two stocks and before recording the outcome, and runs again
- **THEN** the outcome is recorded with the draw positions computed before the stop
