## Purpose

LotteryEntryUseCase.Draw draws one closed Lottery TicketSale, TicketType by TicketType, and records who won before any card is charged.

## ADDED Requirements

### Requirement: Draw a sale without charging

Draw SHALL take a TicketSale. It SHALL read the sale and its TicketTypes with TicketSale.Get, failing with NotFound when it does not exist. For each TicketType it SHALL take the entries from LotteryEntry.ListUndrawnForTicketType, compute the outcome over the Entered entries with LotteryEntry.RunLotteryDraw against the TicketType's quantity, using an unpredictable random order, and record it with LotteryEntry.RecordDrawOutcome. Once every TicketType is recorded, it SHALL record the sale's draw time with TicketSale.RecordDraw. Draw SHALL NOT capture or release any card authorization and SHALL NOT create an Order or a Ticket. A Draft keeps its state and takes no part in the draw.

#### Scenario: Winners and losers recorded
- **WHEN** a closed sale's TicketType with a quantity of 4 has Entered entries for 2, 2 and 3 tickets and the random order admits the two 2-ticket entries
- **THEN** the two 2-ticket entries are Won, the 3-ticket entry is Lost, no card is charged or released by the draw, and the sale is drawn

#### Scenario: Each ticket type is drawn against its own quantity
- **WHEN** a sale has a TicketType of 100 tickets with 80 requested and a TicketType of 4 tickets with 12 requested
- **THEN** every entry of the first TicketType is Won, and the second TicketType's Won entries hold at most 4 tickets

#### Scenario: Losers in draw order
- **WHEN** the draw completes with Lost entries
- **THEN** each Lost entry carries its draw position within its TicketType, so the losers can be read in draw order

#### Scenario: Unconfirmed draft at the draw
- **WHEN** a fan authorized their card for a Draft but never confirmed it, and the window closes
- **THEN** the Draft stays a Draft and takes no part in the draw

#### Scenario: No entries
- **WHEN** the sale has no Draft and no Entered entry
- **THEN** the sale is drawn and no entry changes

### Requirement: A stopped draw resumes with the same outcome

When Draw stops before it recorded the sale's draw time and runs again for the same sale, it SHALL keep the outcome of every TicketType already recorded, draw only the TicketTypes not yet recorded, and then record the draw time.

#### Scenario: Stopped after one ticket type
- **WHEN** Draw stops after recording the first of a sale's two TicketTypes and runs again
- **THEN** the first TicketType keeps its Won and Lost entries, the second is drawn once, and the sale is drawn

### Requirement: Each entry's result is reported

After Draw records an entry Won or Lost, it SHALL send a "lottery result" signal for product analytics for the entry's fan, carrying the TicketSale, the TicketType, the result and the time of the draw as the time it happened. A failure to send it SHALL NOT change the draw.

#### Scenario: Two entries, one place
- **WHEN** Draw admits one of two entries for a TicketType with quantity 1
- **THEN** one Won signal and one Lost signal are sent, each for its entry's fan
