# Spec Delta

## ADDED Requirements

### Requirement: Ticket section shows the sale and its seat types

The ticket section SHALL read the Event's sales with TicketSaleService.ListByEvent and show one of them: the sale whose window is open, otherwise the next to open, otherwise the last that ended. Sales of one event never overlap, so at most one is open. The section SHALL show the sale's name, that one account may hold up to the Event's per-account limit across all sales, with that limit, and each TicketStock of the Event with its seat type's name and price 税込 (tax-inclusive).

For a FirstCome sale:
- before its start time: the sale's start date and time in Japan time;
- within its window, for each TicketStock by its state: Available: an action to buy, adding 残りわずか (few left) when it is LowStock, and never a count; AllHeld: 売り切れ (sold out), with the note that other fans are checking out and that tickets may be available again in a few minutes; SoldOut: 売り切れ;
- after its end time: that the sale has ended.

For a Lottery sale, the section SHALL show its start and end date and time in Japan time and, while its window is open, an action to enter for each TicketStock, which opens the lottery entry screen for that sale and TicketStock; outside the window it shows no action.

For each TicketStock whose resale is open, whichever sale is shown, the section SHALL add 公式リセール (official resale) under that seat type, saying that fans who cannot attend can list their tickets from the tickets screen. It SHALL never show how many tickets are listed.

When the signed-in fan already holds or has applied for tickets of a seat type for the Event, the section SHALL offer actions only for that seat type and SHALL say that one account holds tickets of one seat type per date, naming it. When the Event has no sale, the section SHALL show no sale.

The action to buy or to enter SHALL open the checkout or the entry screen for a signed-in fan. For a guest, it SHALL start sign-up and return to the Event page. The fan's purchased tickets are shown as before.

#### Scenario: On sale with few left

- **WHEN** a guest opens the page of an open first-come sale whose S席, priced 3000 yen, is Available and LowStock
- **THEN** the section shows S席 3,000円（税込）, 残りわずか and the action to buy, with no count

#### Scenario: Two seat types

- **WHEN** an open first-come sale's event has S席 Available and A席 SoldOut
- **THEN** the section shows S席 with the action to buy and A席 as 売り切れ

#### Scenario: Guest buys

- **WHEN** a guest taps the action to buy
- **THEN** sign-up starts and, once it completes, the guest is back on the Event page

#### Scenario: Not yet on sale

- **WHEN** the first-come sale opens on 2026-11-01 10:00
- **THEN** the section shows the opening date and time, each seat type with its price, and no action to buy

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


## REMOVED Requirements

### Requirement: Ticket section shows the sale

**Reason**: Sales now sell TicketStocks of seat types; buying listed tickets moves to the change resell-tickets-by-lottery, which adds its own action.
**Migration**: See "Ticket section shows the sale and its seat types".
