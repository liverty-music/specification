# components/entity/lottery-entry/end-entered-by-event Specification

## Purpose
Ends the lottery entries of a 中止 (cancelled) Event that are still waiting for a draw: each becomes Lost and its Order Void, so nothing can be charged for them.

## Requirements

### Requirement: Every Entered entry of the event ends

EndEnteredByEvent SHALL take an Event and, in one indivisible step, make every Entered LotteryEntry whose Order's TicketStock belongs to that Event Lost with the lost reason "concert cancelled", leaving its draw position absent, and make each of those Orders Void. It SHALL leave a Won or Lost entry, and every entry of another Event, unchanged. An entry a draw records in the same moment SHALL end up either recorded by the draw or ended here, never both. It SHALL succeed and change nothing when the Event has no Entered entry, including when no Event has the id, so calling it again changes nothing.

#### Scenario: Entries of a cancelled event
- **WHEN** an Event's two TicketStocks have three Entered entries and EndEnteredByEvent is called for the Event
- **THEN** all three are Lost with the lost reason "concert cancelled" and no draw position, and their Orders are Void

#### Scenario: Won entry
- **WHEN** an Event has a Won entry whose Order is Pending
- **THEN** that entry and its Order are unchanged

#### Scenario: Another date of the series
- **WHEN** a sale names two Events, each with an Entered entry, and EndEnteredByEvent is called for one of them
- **THEN** the entry of the other Event stays Entered and its Order stays Pending

#### Scenario: Called again
- **WHEN** EndEnteredByEvent is called again for the same Event
- **THEN** it succeeds and nothing changes

#### Scenario: No entries
- **WHEN** the Event has no Entered entry, or no Event has the id
- **THEN** it succeeds and nothing changes

### Requirement: Each ended entry is announced with the change

EndEnteredByEvent SHALL announce each entry it makes Lost as lost (LotteryEntry.Lost), as it is after the change, together with the change: both are stored or neither is. An entry it leaves unchanged SHALL NOT be announced. When an announcement cannot be recorded, EndEnteredByEvent SHALL fail with Unavailable and change nothing. Each announcement is what product analytics records as one "lottery result" signal for the fan of the entry's Order.

#### Scenario: Two entries ended
- **WHEN** EndEnteredByEvent makes two entries Lost
- **THEN** both entries are announced as lost, each carrying its entry Lost with the lost reason "concert cancelled"

#### Scenario: Called again announces nothing
- **WHEN** EndEnteredByEvent is called again for an Event whose entries it already ended
- **THEN** nothing is announced

#### Scenario: Announcement cannot be recorded
- **WHEN** an entry's announcement cannot be recorded
- **THEN** EndEnteredByEvent fails with Unavailable, every entry stays Entered and every Order stays Pending
