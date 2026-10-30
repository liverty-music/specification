# components/usecase/lottery-entry/run-draw Specification

## Purpose
LotteryEntryUseCase.RunDraw draws one closed Lottery TicketSale: for each TicketStock of the events it names it orders the sale's Entered entries at random, admits whole entries that fit the stock's remaining count, captures each winner's card authorization, releases every other card authorization, and records the outcome of the whole sale with the losers' draw order.

## Requirements

### Requirement: Capture failure

When a winner's capture fails, RunDraw SHALL release that entry's card authorization, record it Lost with its draw position so it joins the losers, make its Order Void, and leave its tickets unallocated; no loser is promoted (no 繰上げ, promotion of a loser).

#### Scenario: Winner's card was closed
- **WHEN** CardAuthorization.Capture fails for a winner
- **THEN** its card authorization is released, it is Lost with its draw position, its Order is Void, and its tickets stay unallocated

### Requirement: Release failure does not stop the draw

When releasing a loser's card authorization fails, RunDraw SHALL still record the entry Lost, make its Order Void and continue.

#### Scenario: Release fails for one loser
- **WHEN** CardAuthorization.Release fails for a loser
- **THEN** the entry is still recorded Lost, its Order is Void and the rest of the draw completes

### Requirement: The draw issues nothing

RunDraw SHALL NOT make an Order Paid or create a Ticket; a Won entry's Pending Order is the only input to OrderUseCase.IssueFromCapturedWin.

#### Scenario: After the draw
- **WHEN** RunDraw records an entry Won
- **THEN** its Order is still Pending and no Ticket exists for it yet

### Requirement: Each entry's result is reported

After RunDraw records an entry Won or Lost, it SHALL send a "lottery result" signal for product analytics for the entry's fan, carrying the TicketSale, the TicketStock, the result, for a loss whether it came from a failed capture, and the time of the draw as the time it happened. A failure to send it SHALL NOT change the draw.

#### Scenario: Two entries, one place
- **WHEN** RunDraw admits one of two entries for a TicketStock with 1 remaining ticket
- **THEN** one Won signal and one Lost signal are sent, each for its entry's fan

### Requirement: Draw a sale's entered entries per ticket stock

RunDraw SHALL read the sale and the events it names with TicketSale.Get, failing with NotFound when it does not exist. For each TicketStock of those events, from TicketStock.ListByEvent, it SHALL take the sale's Entered entries for that stock from LotteryEntry.ListEnteredByTicketSaleAndTicketStock and compute the outcome with LotteryEntry.RunLotteryDraw against the stock's remaining count at the draw, read with TicketStock.Get, using an unpredictable random order. It SHALL capture each winner's card authorization with CardAuthorization.Capture, release each loser's card authorization with CardAuthorization.Release, and record the outcome of all stocks with LotteryEntry.PersistDrawOutcome: captured winners Won and every other Entered entry Lost, each with its draw position, and the Order of every Lost entry Void. When the sale has no Entered entry, it SHALL do nothing: the closed sale is already drawn.

#### Scenario: Winners charged, losers released
- **WHEN** a closed sale's stock with 4 remaining tickets has entries for 2, 2 and 3 tickets and the random order admits the two 2-ticket entries
- **THEN** their card authorizations are captured and they are Won, the 3-ticket entry's card authorization is released, it is Lost and its Order is Void, and the sale is drawn

#### Scenario: Each stock is drawn against its own remaining tickets
- **WHEN** a sale's events have an S席 stock with 100 remaining and 80 requested and an A席 stock with 4 remaining and 12 requested
- **THEN** every S席 entry wins, and the A席 winners get at most 4 tickets

#### Scenario: Earlier sales already took tickets
- **WHEN** an S席 stock of 150 sold 120 tickets in a presale and a general lottery has 50 tickets requested
- **THEN** the general lottery's winners get at most 30 tickets

#### Scenario: Losers in draw order
- **WHEN** the draw completes with Lost entries
- **THEN** each Lost entry carries its draw position within its stock, so the losers can be read in draw order

#### Scenario: No entries
- **WHEN** the sale has no Entered entry
- **THEN** nothing is captured, released or recorded, and the sale counts as drawn
