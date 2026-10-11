# Spec Delta

## MODIFIED Requirements

### Requirement: Sale settings with sensible defaults

For an event without a first-come sale, the screen SHALL offer the sale's name, the start time and end time, entered in Japan time, the price per ticket 税込 (tax-inclusive), the quantity and the per-account limit, with the name defaulting to 一般発売, the end time defaulting to the event's start time and the limit defaulting to 4. Saving SHALL create a FirstCome sale of the event's Series with one TicketType for the event, with TicketSaleService.Create. It SHALL show an error next to a field, without saving, when the end time is after the event's start time, the end is not after the start, the name is empty or longer than 100 characters, the price is outside 1 to 1,000,000 yen, the quantity is below 1, or the limit is outside 1 to 10 or above the quantity. When saving fails because the window overlaps another sale of the event, the screen SHALL say so.

#### Scenario: Blank form

- **WHEN** an operator opens the editor for an event starting 2026-11-20 19:00
- **THEN** the end time is 2026-11-20 19:00, the name is 一般発売 and the limit is 4

#### Scenario: End after the show starts

- **WHEN** the operator sets the end time to 19:30 for a 19:00 show and saves
- **THEN** an error is shown next to the end time and nothing is saved

#### Scenario: Overlapping a presale

- **WHEN** the event's lottery presale runs to 10 November and the operator saves a sale starting 8 November
- **THEN** the screen says the window overlaps another sale and nothing is saved

### Requirement: What can change once the sale has started

For an event with a first-come sale, read with TicketSaleService.ListByEvent, the screen SHALL show the quantity, the sold count and the held count of its TicketType. A change to the start or end time SHALL be saved with TicketSaleService.SetWindow, and a change to the price, quantity or per-account limit with TicketTypeService.Update. While any ticket is sold or held, it SHALL show the price as fixed, and it SHALL refuse a quantity below what is sold and held, saying why.

#### Scenario: Price locked

- **WHEN** the operator opens the editor while a fan's checkout holds 2 tickets
- **THEN** the price cannot be edited and the screen says it is fixed while tickets are held or sold

#### Scenario: More tickets

- **WHEN** the operator raises the quantity from 150 to 180 and saves
- **THEN** the TicketType is updated and the screen shows a quantity of 180

#### Scenario: Sale extended

- **WHEN** the operator moves the end time later, still no later than the event's start time, and saves
- **THEN** the sale's window is updated and the price, quantity and limit are unchanged

### Requirement: Prerequisites explained

When the event is not published, has no start time, or the Organizer does not have complete business details, the screen SHALL say which is missing and not offer to save. For missing business details, it SHALL say they are entered by Liverty Music during vetting.

#### Scenario: No start time

- **WHEN** the operator opens the editor for an event without a start time
- **THEN** the screen says to set the start time in the concert editor first and links to it
