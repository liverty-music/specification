## Purpose

LotteryEntryUseCase.Draw draws one closed Lottery TicketSale and records who won and who lost, before any card is charged or released.

## ADDED Requirements

### Requirement: Draw a sale without charging

Draw SHALL take a TicketSale. It SHALL read the sale and its TicketTypes with TicketSale.Get, failing with NotFound when it does not exist. For each TicketType it SHALL take the Entered entries from LotteryEntry.ListUndrawnForTicketType and compute the outcome with LotteryEntry.RunLotteryDraw against the TicketType's quantity, using an unpredictable random order. It SHALL then record the outcome of all TicketTypes with LotteryEntry.PersistDrawOutcome: the admitted entries Won and every other Entered entry Lost, each with its draw position. When the sale has no Entered entry, it SHALL only mark the sale drawn. Draw SHALL NOT capture or release any card authorization and SHALL NOT create an Order or a Ticket; no loser is promoted (no 繰上げ, promotion of a loser).

#### Scenario: Winners and losers recorded
- **WHEN** a closed sale's TicketType with a quantity of 4 has Entered entries for 2, 2 and 3 tickets and the random order admits the two 2-ticket entries
- **THEN** the two 2-ticket entries are Won, the 3-ticket entry is Lost, no card is charged or released by the draw, and the sale is drawn

#### Scenario: Each ticket type is drawn against its own quantity
- **WHEN** a sale has a TicketType of 100 tickets with 80 requested and a TicketType of 4 tickets with 12 requested
- **THEN** every entry of the first TicketType is Won, and the second TicketType's Won entries hold at most 4 tickets

#### Scenario: Losers in draw order
- **WHEN** the draw completes with Lost entries
- **THEN** each Lost entry carries its draw position within its TicketType, so the losers can be read in draw order

#### Scenario: No entries
- **WHEN** the sale has no Entered entry
- **THEN** the sale is drawn and no entry changes

### Requirement: A stopped draw resumes with the same outcome

The random order of a draw SHALL be computed once. When Draw stops and runs again for the same sale, it SHALL record the outcome it computed before, never a new one.

#### Scenario: Stopped before the outcome was recorded
- **WHEN** Draw stops after computing the outcome of a sale's two TicketTypes and before recording it, and runs again
- **THEN** the recorded Won and Lost entries are the ones computed before the stop

### Requirement: Each entry's result is announced

After the outcome is recorded, Draw SHALL announce each entry's lottery result for the entry's fan, carrying the entry, the TicketSale, the TicketType, the result and the time of the draw as the time it happened. When announcing fails, Draw SHALL try again; a failure to announce never changes the recorded outcome.

#### Scenario: Two entries, one place
- **WHEN** Draw admits one of two entries for a TicketType with quantity 1
- **THEN** one Won result and one Lost result are announced, each for its entry's fan
