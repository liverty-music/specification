# Lottery Sale Editor

## Purpose

The organizer console screen where an operator puts one published event on sale by lottery: the sale's name and window, and its TicketType's quantity, per-account limit and price.

## Requirements

### Requirement: The sale window defaults to 10 days

A new lottery sale form SHALL open with the window starting now and closing 10 days later. The screen SHALL accept a window of 1 to 14 days and SHALL show an error next to the window, without saving, for any other length.

#### Scenario: Blank form

- **WHEN** an operator opens the lottery sale editor for an event without a sale at 2026-10-01 12:00
- **THEN** the window opens at 2026-10-01 12:00 and closes at 2026-10-11 12:00

#### Scenario: Window too long

- **WHEN** the operator sets a window of 15 days and saves
- **THEN** an error is shown next to the window and nothing is saved

### Requirement: An event goes on sale only with its start time

When the event has no start time, the lottery sale editor SHALL say that the start time must be set in the concert editor before the event can go on sale, link to the concert editor, and SHALL not save the sale. An event without an open time SHALL go on sale as usual.

#### Scenario: Start time not set

- **WHEN** an operator opens the lottery sale editor for a published event with no start time
- **THEN** the screen says the start time must be set first, links to the concert editor, and saving is not offered

### Requirement: The editor creates a named lottery sale for one event

The editor SHALL create a Lottery TicketSale for the event it was opened from, with a name, the window, and one TicketType for that event with a quantity, a per-account limit and a price. The name SHALL be required, and the per-account limit SHALL default to 4 and accept 1 to 10. When a sale of the event already overlaps the entered window, the screen SHALL say so next to the window and SHALL not save.

#### Scenario: Presale for one event
- **WHEN** an operator names the sale ファンクラブ先行, keeps the 10-day window and enters 100 tickets at 8000 yen
- **THEN** a Lottery sale named ファンクラブ先行 is created with one TicketType of 100 tickets at 8000 yen and a per-account limit of 4

#### Scenario: Missing name
- **WHEN** the operator saves without a name
- **THEN** an error is shown next to the name and nothing is saved

#### Scenario: Overlapping window
- **WHEN** the event already has a sale from 1 to 10 November and the operator enters a window starting 8 November
- **THEN** the screen says the window overlaps that sale and nothing is saved

### Requirement: Opened from the event's Sales tab and back

The lottery sale editor SHALL be opened from 抽選で販売する on an event's Sales tab, or from 編集 on one of the event's lottery sales, SHALL show that event's date, start time and venue, and SHALL have the event as its parent in the breadcrumb. After the sale is created or changed the console SHALL return to the event's Sales tab; leaving without saving SHALL return there too, guarding unsaved changes.

#### Scenario: Back after creating

- **WHEN** an operator creates a lottery sale from the Sales tab of the 3 November event
- **THEN** the Sales tab of the 3 November event opens and lists the new sale

#### Scenario: Breadcrumb

- **WHEN** the editor is open for the 3 November event of XX Tour 2026
- **THEN** the breadcrumb reads 公演 › XX Tour 2026 › 11月3日(火) › 抽選で販売

### Requirement: The window is entered in Japan time

The editor SHALL take the sale's start and end as Japan time, marked JST, whatever the device's time zone, and SHALL show the price with yen separators.

#### Scenario: Device in another time zone

- **WHEN** an operator whose device is set to London time enters a start of 2026-10-10 12:00 JST and saves
- **THEN** the sale opens at 12:00 Japan time on 10 October

### Requirement: A lottery sale changes only before it opens

Opened with 編集 for a lottery sale, the editor SHALL show the sale's name without letting it change, and SHALL let the operator change the window, the price, the quantity and the per-account limit under the same rules as a new sale. It SHALL save the window with TicketSaleService.SetWindow and the price, quantity and per-account limit with TicketTypeService.Update. When the sale has opened by the time the operator saves, the editor SHALL say that a lottery cannot change once its window has opened and SHALL save nothing.

#### Scenario: Move the window before it opens

- **WHEN** an operator moves an unopened lottery's window from 10 to 17 October to 12 to 19 October and saves
- **THEN** the sale opens on 12 October and the Sales tab shows the new window

#### Scenario: Change the price before it opens

- **WHEN** an operator changes an unopened lottery's price from 8000 to 7500 yen and saves
- **THEN** the sale's TicketType costs 7500 yen

#### Scenario: Sale opened while editing

- **WHEN** an operator saves a change after the lottery's window has opened
- **THEN** the editor says the lottery cannot change once its window has opened and nothing is saved
