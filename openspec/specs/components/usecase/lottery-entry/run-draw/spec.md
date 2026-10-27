# components/usecase/lottery-entry/run-draw Specification

## Purpose
LotteryEntryUseCase.RunDraw draws one closed Lottery TicketSale: for each of its TicketTypes it orders the Entered entries at random, admits whole entries that fit the TicketType's quantity, captures each winner's card authorization, releases every other card authorization, and records the outcome of the whole sale with the losers' draw order.

## Requirements

### Requirement: Capture failure

When a winner's capture fails, RunDraw SHALL release that entry's card authorization, record it Lost with its draw position so it joins the losers, and leave its tickets unallocated; no loser is promoted (no 繰上げ, promotion of a loser).

#### Scenario: Winner's card was closed
- **WHEN** CardAuthorization.Capture fails for a winner
- **THEN** its card authorization is released, it is Lost with its draw position, and its tickets stay unallocated

### Requirement: Release failure does not stop the draw

When releasing a loser's card authorization fails, RunDraw SHALL still record the entry Lost and continue.

#### Scenario: Release fails for one loser
- **WHEN** CardAuthorization.Release fails for a loser
- **THEN** the entry is still recorded Lost and the rest of the draw completes

### Requirement: The draw issues nothing

RunDraw SHALL NOT create an Order or a Ticket; a Won entry is the only input to OrderUseCase.IssueFromCapturedWin.

#### Scenario: After the draw
- **WHEN** RunDraw records an entry Won
- **THEN** no Order or Ticket exists for it yet

### Requirement: Each entry's result is reported

After RunDraw records an entry Won or Lost, it SHALL send a "lottery result" signal for product analytics for the entry's fan, carrying the TicketSale, the TicketType, the result, for a loss whether it came from a failed capture, and the time of the draw as the time it happened. A failure to send it SHALL NOT change the draw.

#### Scenario: Two entries, one place
- **WHEN** RunDraw admits one of two entries for a TicketType with quantity 1
- **THEN** one Won signal and one Lost signal are sent, each for its entry's fan

### Requirement: Draw a sale's entered entries

RunDraw SHALL read the sale and its TicketTypes with TicketSale.Get, failing with NotFound when it does not exist. For each TicketType it SHALL take the Entered entries from LotteryEntry.ListUndrawnForTicketType and compute the outcome with LotteryEntry.RunLotteryDraw against the TicketType's quantity, using an unpredictable random order. It SHALL capture each winner's card authorization with CardAuthorization.Capture, release each loser's card authorization with CardAuthorization.Release, and record the outcome of all TicketTypes with LotteryEntry.PersistDrawOutcome: captured winners Won and every other Entered entry Lost, each with its draw position. When the sale has no Entered entry, it SHALL only mark the sale drawn.

#### Scenario: Winners charged, losers released
- **WHEN** a closed sale's TicketType with a quantity of 4 has entries for 2, 2 and 3 tickets and the random order admits the two 2-ticket entries
- **THEN** their card authorizations are captured and they are Won, the 3-ticket entry's card authorization is released and it is Lost, and the sale is drawn

#### Scenario: Each ticket type is drawn against its own quantity
- **WHEN** a sale has a TicketType of 100 tickets with 80 requested and a TicketType of 4 tickets with 12 requested
- **THEN** every entry of the first TicketType wins, and the second TicketType's winners get at most 4 tickets

#### Scenario: Losers in draw order
- **WHEN** the draw completes with Lost entries
- **THEN** each Lost entry carries its draw position within its TicketType, so the losers can be read in draw order

#### Scenario: No entries
- **WHEN** the sale has no Entered entry
- **THEN** the sale is marked drawn and nothing is captured or released
