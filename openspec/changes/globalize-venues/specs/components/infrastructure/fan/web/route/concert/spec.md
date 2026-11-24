## MODIFIED Requirements

### Requirement: What the concert page shows

For an event with a concert page, the Concert page SHALL show:
- the Series' cover image, or a brand placeholder when there is none;
- the Series' title;
- each performing Artist's name with a follow control;
- the date with weekday, the doors-open and start times when announced, each written as "OPEN" and "START", at the Venue's local time, labelled as global/i18n "Each kind of time is shown in the zone it belongs to" states for an Event's times (the Venue zone's name and the fan's own times when the fan's browser zone has another offset);
- the venue name and its prefecture as a localized name (never the raw code), with a link that opens the venue in Google Maps;
- the Series' description, when present;
- a share control and an add-to-calendar control;
- a ticket section.

Text the Organizer entered (title, description, venue as listed) SHALL be shown as entered in every display language; labels, dates and times SHALL follow the app's display language. The add-to-calendar control SHALL add the event at its Venue's local time in the Venue's time zone. The page SHALL NOT show the ticket journey status control.

#### Scenario: Event without a cover image

- **WHEN** the Series has no cover image
- **THEN** the page shows the brand placeholder in its place

#### Scenario: Start time not announced

- **WHEN** the event has a doors-open time of 18:30 at a Venue in Tokyo, no start time, and the fan's browser is set to Japan time
- **THEN** the page shows "OPEN 18:30" and no START time

#### Scenario: English display language

- **WHEN** the display language is English and the Organizer wrote the title in Japanese
- **THEN** the title is shown in Japanese and the date and labels in English

#### Scenario: Event abroad

- **WHEN** a fan whose browser is set to Japan time opens an event on 2027-02-20 at a Venue in London with OPEN 18:30 and START 19:30
- **THEN** the page shows 2月20日(土), OPEN 18:30 and START 19:30 with ロンドン時間, and the Japan times 2月21日(日) 03:30 and 04:30 in parentheses

#### Scenario: Event in Japan seen from Japan

- **WHEN** a fan whose browser is set to Japan time opens an event at a Venue in Tokyo with OPEN 17:00 and START 18:00
- **THEN** the page shows OPEN 17:00 and START 18:00 with no zone

#### Scenario: Add an event abroad to a calendar

- **WHEN** a fan whose browser is set to Japan time adds an event that starts on 2027-02-20 at 19:30 at a Venue in London to their calendar
- **THEN** the calendar entry starts at 19:30 in the London time zone, which the fan's calendar shows as 04:30 on 21 February in Japan time

### Requirement: Ticket section shows the sale and its seat types

The ticket section SHALL read the Event's sales with TicketSaleService.ListByEvent and show one of them: the sale whose window is open, otherwise the next to open, otherwise the last that ended. Sales of one event never overlap, so at most one is open. The section SHALL show the sale's name, that one account may hold up to the Event's per-account limit across all sales, with that limit, and each TicketStock of the Event with its seat type's name and price 税込 (tax-inclusive). Every sale date and time SHALL be shown in the fan's browser time zone, with that zone's name when it is not the sale's time zone (global/i18n "Each kind of time is shown in the zone it belongs to").

For a FirstCome sale:
- before its start time: the sale's start date and time;
- within its window, for each TicketStock by its state: Available: an action to buy, adding 残りわずか (few left) when it is LowStock, and never a count; AllHeld: 売り切れ (sold out), with the note that other fans are checking out and that tickets may be available again in a few minutes; SoldOut: 売り切れ;
- after its end time: that the sale has ended.

For a Lottery sale, the section SHALL show its start and end date and time and, while its window is open, an action to enter for each TicketStock, which opens the lottery entry screen for that sale and TicketStock; outside the window it shows no action.

For each TicketStock whose resale is open, whichever sale is shown, the section SHALL add 公式リセール (official resale) under that seat type, saying that fans who cannot attend can list their tickets from the tickets screen. It SHALL never show how many tickets are listed.

When the signed-in fan already holds or has applied for tickets of a seat type for the Event, the section SHALL offer actions only for that seat type and SHALL say that one account holds tickets of one seat type per date, naming it. When the Event has no sale, the section SHALL show no sale.

The action to buy or to enter SHALL open the checkout or the entry screen for a signed-in fan. For a guest, it SHALL start sign-up and return to the Concert page. The fan's purchased tickets are shown as before.

#### Scenario: On sale with few left

- **WHEN** a guest opens the page of an open first-come sale whose S席, priced 3000 yen, is Available and LowStock
- **THEN** the section shows S席 3,000円（税込）, 残りわずか and the action to buy, with no count

#### Scenario: Two seat types

- **WHEN** an open first-come sale's event has S席 Available and A席 SoldOut
- **THEN** the section shows S席 with the action to buy and A席 as 売り切れ

#### Scenario: Guest buys

- **WHEN** a guest taps the action to buy
- **THEN** sign-up starts and, once it completes, the guest is back on the Concert page

#### Scenario: Not yet on sale

- **WHEN** the first-come sale in the time zone Asia/Tokyo opens on 2026-11-01 10:00 and the fan's browser is set to Japan time
- **THEN** the section shows 11月1日(日) 10:00 with no zone, each seat type with its price, and no action to buy

#### Scenario: Sale abroad seen from Japan

- **WHEN** the first-come sale in the time zone Asia/Taipei opens on 2027-02-01 12:00 and the fan's browser is set to Japan time
- **THEN** the section shows the opening as 2月1日(月) 13:00 日本時間

#### Scenario: Temporarily all held

- **WHEN** the open first-come sale's S席 is AllHeld
- **THEN** the section shows S席 as 売り切れ with the note that tickets may be available again in a few minutes

#### Scenario: Sold out with resale open

- **WHEN** S席, priced 5000 yen, is SoldOut and its resale is open
- **THEN** the section shows S席 as 売り切れ and 公式リセール with the note that tickets can be listed from the tickets screen, and no action to buy

#### Scenario: Fan already holds another seat type

- **WHEN** a signed-in fan holds 2 S席 tickets for the event and opens the page of an open sale with S席 and A席 Available
- **THEN** the section offers the action to buy for S席 only and says the fan's tickets for this date are S席

#### Scenario: Presale over, general sale upcoming

- **WHEN** a lottery presale ended on 10 November and a first-come general sale opens on 20 November, and the fan opens the page on 15 November
- **THEN** the section shows the general sale's name and its opening date and time

#### Scenario: Lottery open

- **WHEN** a lottery sale named ファンクラブ先行 is open, with S席 priced 8000 yen
- **THEN** the section shows ファンクラブ先行, its window, S席 8,000円（税込） and the action to enter, which opens the entry screen for that sale and S席

#### Scenario: Every sale ended

- **WHEN** the presale and the general sale have both ended
- **THEN** the section shows the general sale as ended

#### Scenario: No sale

- **WHEN** no sale names the Event
- **THEN** the section shows no sale
