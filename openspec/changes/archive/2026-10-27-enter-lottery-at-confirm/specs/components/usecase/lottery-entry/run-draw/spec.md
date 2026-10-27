## ADDED Requirements

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

## REMOVED Requirements

### Requirement: Draw a sale
**Reason**: There are no Drafts to release or withdraw at the draw.
**Migration**: Replaced by "Draw a sale's entered entries".
