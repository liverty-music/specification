# Spec Delta

## Purpose

LotteryUseCase.RunDraw draws one closed Lottery TicketSale: for each of its TicketTypes it orders the Entered entries at random, admits whole entries that fit the TicketType's quantity, captures each winner's hold, releases every other hold, and records the outcome of the whole sale with the losers' draw order.

## ADDED Requirements

### Requirement: Draw a sale

RunDraw SHALL read the sale and its TicketTypes with TicketSale.Get, failing with NotFound when it does not exist. For each TicketType it SHALL take the Entered entries from LotteryEntry.ListEnteredForTicketType and compute the outcome with LotteryEntry.RunLotteryDraw against the TicketType's quantity, using an unpredictable random order. It SHALL capture each winner's hold with LotteryEntry.CaptureAuthorization, release each waitlisted entry's hold with LotteryEntry.CancelAuthorization, and record the outcome of all TicketTypes with LotteryEntry.PersistDrawOutcome: captured winners Won, every other entry Lost, each with its draw position. When the sale has no Entered entry, it SHALL only mark the sale drawn.

#### Scenario: Winners charged, losers released
- **WHEN** a closed sale's TicketType with a quantity of 4 has entries for 2, 2 and 3 tickets and the random order admits the two 2-ticket entries
- **THEN** their holds are captured and they are Won, the 3-ticket entry's hold is released and it is Lost, and the sale is drawn

#### Scenario: Each ticket type is drawn against its own quantity
- **WHEN** a sale has a TicketType of 100 tickets with 80 requested and a TicketType of 4 tickets with 12 requested
- **THEN** every entry of the first TicketType wins, and the second TicketType's winners hold at most 4 tickets

#### Scenario: Losers ordered for the waitlist
- **WHEN** the draw completes with Lost entries
- **THEN** each Lost entry carries its draw position within its TicketType, so the waitlist can be read in draw order

#### Scenario: No entries
- **WHEN** the sale has no Entered entry
- **THEN** the sale is marked drawn and nothing is captured or released

### Requirement: Capture failure

When a winner's capture fails, RunDraw SHALL release that entry's hold, record it Lost with its draw position so it joins the waitlist, and leave its tickets unallocated; no waitlisted entry is promoted (no 繰上げ, promotion from the waitlist).

#### Scenario: Winner's card was closed
- **WHEN** LotteryEntry.CaptureAuthorization fails for a winner
- **THEN** its hold is released, it is Lost with its draw position, and its tickets stay unallocated

### Requirement: Release failure does not stop the draw

When releasing a loser's hold fails, RunDraw SHALL still record the entry Lost and continue.

#### Scenario: Release fails for one loser
- **WHEN** LotteryEntry.CancelAuthorization fails for a waitlisted entry
- **THEN** the entry is still recorded Lost and the rest of the draw completes

### Requirement: The draw issues nothing

RunDraw SHALL NOT create an Order or a Ticket; a Won entry is the only input to IssuanceUseCase.IssueFromCapturedWin.

#### Scenario: After the draw
- **WHEN** RunDraw records an entry Won
- **THEN** no Order or Ticket exists for it yet
