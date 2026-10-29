# Ticket Sale Editor

## Purpose

The organizer console screen where a member puts one published event on sale, by lottery or first come, first served, or changes that sale: the sale's name and window. The sale sells the event's TicketStocks, each a seat type with its price and quantity, under the event's per-account limit; the screen shows them but does not change them.

## Requirements

### Requirement: A first-come sale's settings and defaults

For an event without a first-come sale, the screen SHALL offer the sale's name, the start time and end time, entered in Japan time, the price per ticket 税込 (tax-inclusive), the quantity and the per-account limit, with the name defaulting to 一般発売, the end time defaulting to the event's start time and the limit defaulting to 4. Saving SHALL create a FirstCome sale of the event's Series with one TicketType for the event, with TicketSaleService.Create. It SHALL show an error next to a field, without saving, when the end time is after the event's start time, the end is not after the start, the name is empty or longer than 100 characters, the price is outside 1 to 1,000,000 yen, the quantity is below 1, or the limit is outside 1 to 10 or above the quantity. When saving fails because the window overlaps another sale of the event, the screen SHALL say so.

#### Scenario: Blank form

- **WHEN** a member opens the editor for an event starting 2026-11-20 19:00
- **THEN** the end time is 2026-11-20 19:00, the name is 一般発売 and the limit is 4

#### Scenario: End after the show starts

- **WHEN** the member sets the end time to 19:30 for a 19:00 show and saves
- **THEN** an error is shown next to the end time and nothing is saved

#### Scenario: Overlapping a presale

- **WHEN** the event's lottery presale runs to 10 November and the member saves a sale starting 8 November
- **THEN** the screen says the window overlaps another sale and nothing is saved

### Requirement: What can change once a first-come sale has started

For an event with a first-come sale, read with TicketSaleService.ListByEvent, the screen SHALL show the quantity, the sold count and the held count of its TicketType. A change to the start or end time SHALL be saved with TicketSaleService.SetWindow, and a change to the price, quantity or per-account limit with TicketTypeService.Update. While any ticket is sold or held, it SHALL show the price as fixed, and it SHALL refuse a quantity below what is sold and held, saying why.

#### Scenario: Price locked

- **WHEN** the member opens the editor while a fan's checkout holds 2 tickets
- **THEN** the price cannot be edited and the screen says it is fixed while tickets are held or sold

#### Scenario: More tickets

- **WHEN** the member raises the quantity from 150 to 180 and saves
- **THEN** the TicketType is updated and the screen shows a quantity of 180

#### Scenario: Sale extended

- **WHEN** the member moves the end time later, still no later than the event's start time, and saves
- **THEN** the sale's window is updated and the price, quantity and limit are unchanged

### Requirement: Prerequisites explained

When the event is not published, has no start time, or the Organizer does not have complete business details, the screen SHALL say which is missing and not offer to save. For missing business details, it SHALL say they are entered by Liverty Music during vetting. Each of these notices SHALL also link to the members' guide, opened in a new tab, at the chapter that explains it: 公演をつくって公開する for an unpublished event or a missing start time, and 事業者情報と受取口座 for incomplete business details.

#### Scenario: No start time

- **WHEN** the member opens the editor for an event without a start time
- **THEN** the screen says to set the start time in the concert editor first and links to it and to the guide's chapter 公演をつくって公開する

#### Scenario: Business details incomplete

- **WHEN** the member opens the editor for a published, timed event of an Organizer without a business phone number
- **THEN** the screen says the business details are entered by Liverty Music during vetting, links to the guide's chapter 事業者情報と受取口座, and saving is not offered

### Requirement: A lottery window defaults to 10 days

A new lottery sale SHALL open with the window starting now and closing 10 days later. The screen SHALL accept a window of 1 to 14 days and SHALL show an error next to the window, without saving, for any other length.

#### Scenario: Blank lottery form

- **WHEN** a member opens the editor for a lottery sale for an event without a sale at 2026-10-01 12:00
- **THEN** the window opens at 2026-10-01 12:00 and closes at 2026-10-11 12:00

#### Scenario: Window too long

- **WHEN** the member sets a window of 15 days and saves
- **THEN** an error is shown next to the window and nothing is saved

### Requirement: An event goes on sale only with its start time

When the event has no start time, the editor SHALL, for a lottery sale, say that the start time must be set in the concert editor before the event can go on sale, link to the concert editor, and SHALL not save the sale. An event without an open time SHALL go on sale as usual.

#### Scenario: Start time not set

- **WHEN** a member opens the editor for a lottery sale for a published event with no start time
- **THEN** the screen says the start time must be set first, links to the concert editor, and saving is not offered

### Requirement: The editor creates a named lottery sale for one event

The editor SHALL create a Lottery TicketSale for the event it was opened from, with a name, the window, and one TicketType for that event with a quantity, a per-account limit and a price. The name SHALL be required, and the per-account limit SHALL default to 4 and accept 1 to 10. When a sale of the event already overlaps the entered window, the screen SHALL say so next to the window and SHALL not save.

#### Scenario: Presale for one event
- **WHEN** a member names the sale ファンクラブ先行, keeps the 10-day window and enters 100 tickets at 8000 yen
- **THEN** a Lottery sale named ファンクラブ先行 is created with one TicketType of 100 tickets at 8000 yen and a per-account limit of 4

#### Scenario: Missing name
- **WHEN** the member saves without a name
- **THEN** an error is shown next to the name and nothing is saved

#### Scenario: Overlapping window
- **WHEN** the event already has a sale from 1 to 10 November and the member enters a window starting 8 November
- **THEN** the screen says the window overlaps that sale and nothing is saved

### Requirement: Opened from the event's Sales tab and back

The editor for a lottery sale SHALL be opened from 抽選で販売する on an event's Sales tab, or from 編集 on one of the event's lottery sales, SHALL show that event's date, start time and venue, and SHALL have the event as its parent in the breadcrumb. After the sale is created or changed the console SHALL return to the event's Sales tab; leaving without saving SHALL return there too, guarding unsaved changes.

#### Scenario: Back after creating

- **WHEN** a member creates a lottery sale from the Sales tab of the 3 November event
- **THEN** the Sales tab of the 3 November event opens and lists the new sale

#### Scenario: Breadcrumb

- **WHEN** the editor is open for the 3 November event of XX Tour 2026
- **THEN** the breadcrumb reads 公演 › XX Tour 2026 › 11月3日(火) › 抽選で販売

### Requirement: A lottery window is entered in Japan time

The editor SHALL take the sale's start and end as Japan time, marked JST, whatever the device's time zone, and SHALL show the price with yen separators.

#### Scenario: Device in another time zone

- **WHEN** a member whose device is set to London time enters a start of 2026-10-10 12:00 JST and saves
- **THEN** the sale opens at 12:00 Japan time on 10 October

### Requirement: A lottery sale changes only before it opens

Opened with 編集 for a lottery sale, the editor SHALL show the sale's name without letting it change, and SHALL let the member change the window, the price, the quantity and the per-account limit under the same rules as a new sale. It SHALL save the window with TicketSaleService.SetWindow and the price, quantity and per-account limit with TicketTypeService.Update. When the sale has opened by the time the member saves, the editor SHALL say that a lottery cannot change once its window has opened and SHALL save nothing.

#### Scenario: Move the window before it opens

- **WHEN** a member moves an unopened lottery's window from 10 to 17 October to 12 to 19 October and saves
- **THEN** the sale opens on 12 October and the Sales tab shows the new window

#### Scenario: Change the price before it opens

- **WHEN** a member changes an unopened lottery's price from 8000 to 7500 yen and saves
- **THEN** the sale's TicketType costs 7500 yen

#### Scenario: Sale opened while editing

- **WHEN** a member saves a change after the lottery's window has opened
- **THEN** the editor says the lottery cannot change once its window has opened and nothing is saved
