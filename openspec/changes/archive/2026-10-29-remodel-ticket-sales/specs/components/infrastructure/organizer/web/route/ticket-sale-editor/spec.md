# Spec Delta

## MODIFIED Requirements

### Requirement: A first-come sale's settings and defaults

For an event without a first-come sale, the screen SHALL offer the sale's name and the start time and end time, entered in Japan time, with the name defaulting to 一般発売 and the end time defaulting to the event's start time. It SHALL list the event's TicketStocks the sale will sell, each with its seat type's name and price 税込 (tax-inclusive) and its quantity, and SHALL say that the sale sells every seat type of the event and that the per-account limit is the event's, with that limit. Saving SHALL create a FirstCome sale of the event's Series naming the event, with TicketSaleService.Create. It SHALL show an error next to a field, without saving, when the end time is after the event's start time, the end is not after the start, or the name is empty or longer than 100 characters. When saving fails because the window overlaps another sale of the event, the screen SHALL say so.

#### Scenario: Blank form

- **WHEN** a member opens the editor for an event starting 2026-11-20 19:00 with the TicketStocks S席 8,000円 × 300 and A席 6,000円 × 700 and a per-account limit of 4
- **THEN** the end time is 2026-11-20 19:00, the name is 一般発売, and the screen lists S席 and A席 and says up to 4 tickets per account

#### Scenario: End after the show starts

- **WHEN** the member sets the end time to 19:30 for a 19:00 show and saves
- **THEN** an error is shown next to the end time and nothing is saved

#### Scenario: Overlapping a presale

- **WHEN** the event's lottery presale runs to 10 November and the member saves a sale starting 8 November
- **THEN** the screen says the window overlaps another sale and nothing is saved

### Requirement: Prerequisites explained

When the event is not published, has no start time, has no TicketStock, or the Organizer does not have complete business details, the screen SHALL say which is missing and not offer to save. For a missing TicketStock, it SHALL link to the event's Sales tab, where stocks are added. For missing business details, it SHALL say they are entered by Liverty Music during vetting. Each of these notices SHALL also link to the members' guide, opened in a new tab, at the chapter that explains it: 公演をつくって公開する for an unpublished event or a missing start time, チケットを販売する for a missing TicketStock, and 事業者情報と受取口座 for incomplete business details.

#### Scenario: No start time

- **WHEN** the member opens the editor for an event without a start time
- **THEN** the screen says to set the start time in the concert editor first and links to it and to the guide's chapter 公演をつくって公開する

#### Scenario: No seat type stocked

- **WHEN** the member opens the editor for a published, timed event without a TicketStock
- **THEN** the screen says to add seat types and quantities to the event first, links to the event's Sales tab and to the guide's chapter チケットを販売する, and saving is not offered

#### Scenario: Business details incomplete

- **WHEN** the member opens the editor for a published, timed event of an Organizer without a business phone number
- **THEN** the screen says the business details are entered by Liverty Music during vetting, links to the guide's chapter 事業者情報と受取口座, and saving is not offered

### Requirement: The editor creates a named lottery sale for one event

The editor SHALL create a Lottery TicketSale naming the event it was opened from, with a name and the window. It SHALL list the event's TicketStocks the sale will draw from, each with its seat type's name and price 税込 and its quantity, and say that the per-account limit is the event's, with that limit. The name SHALL be required. When a sale of the event already overlaps the entered window, the screen SHALL say so next to the window and SHALL not save.

#### Scenario: Presale for one event
- **WHEN** a member names the sale ファンクラブ先行 and keeps the 10-day window for an event with the TicketStock S席 8,000円 × 100
- **THEN** a Lottery sale named ファンクラブ先行 naming the event is created, and it draws from S席

#### Scenario: Missing name
- **WHEN** the member saves without a name
- **THEN** an error is shown next to the name and nothing is saved

#### Scenario: Overlapping window
- **WHEN** the event already has a sale from 1 to 10 November and the member enters a window starting 8 November
- **THEN** the screen says the window overlaps that sale and nothing is saved

### Requirement: A lottery window is entered in Japan time

The editor SHALL take the sale's start and end as Japan time, marked JST, whatever the device's time zone, and SHALL show the seat types' prices with yen separators.

#### Scenario: Device in another time zone

- **WHEN** a member whose device is set to London time enters a start of 2026-10-10 12:00 JST and saves
- **THEN** the sale opens at 12:00 Japan time on 10 October

## ADDED Requirements

### Requirement: Only the window of a first-come sale changes

For an event with a first-come sale, read with TicketSaleService.ListByEvent, the screen SHALL show the sale's name and window. A change to the start or end time SHALL be saved with TicketSaleService.SetWindow. Nothing else SHALL be changeable: the seat types and quantities are the event's TicketStocks, which never change.

#### Scenario: Sale extended

- **WHEN** the member moves the end time later, still no later than the event's start time, and saves
- **THEN** the sale's window is updated

#### Scenario: Nothing else to edit

- **WHEN** the member opens the editor for an event with a first-come sale
- **THEN** the screen offers the window only, and no price, quantity or per-account limit

### Requirement: Only the window of a lottery sale changes, before it opens

Opened with 編集 for a lottery sale, the editor SHALL show the sale's name without letting it change, and SHALL let the member change the window under the same rules as a new sale, saving it with TicketSaleService.SetWindow. When the sale has opened by the time the member saves, the editor SHALL say that a lottery cannot change once its window has opened and SHALL save nothing.

#### Scenario: Move the window before it opens

- **WHEN** a member moves an unopened lottery's window from 10 to 17 October to 12 to 19 October and saves
- **THEN** the sale opens on 12 October and the Sales tab shows the new window

#### Scenario: Sale opened while editing

- **WHEN** a member saves a change after the lottery's window has opened
- **THEN** the editor says the lottery cannot change once its window has opened and nothing is saved

## REMOVED Requirements

### Requirement: What can change once a first-come sale has started

**Reason**: Price, quantity and per-account limit are no longer on the sale: the seat types, their prices and quantities are fixed TicketStocks of the event, and the limit is the event's.
**Migration**: See "Only the window of a first-come sale changes".

### Requirement: A lottery sale changes only before it opens

**Reason**: Only the window remains on the sale; price, quantity and per-account limit moved to SeatType, TicketStock and Event, which never change.
**Migration**: See "Only the window of a lottery sale changes, before it opens".
