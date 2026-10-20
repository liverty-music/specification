## MODIFIED Requirements

### Requirement: Ticket section shows the sale

The ticket section SHALL read the Event's sales with TicketSaleService.ListByEvent and show one of them: the sale whose window is open, otherwise the next to open, otherwise the last that ended. Sales of one event never overlap, so at most one is open. The section SHALL show the sale's name and its TicketType for the Event and, for a FirstCome sale, by the TicketType's state:
- NotYetOnSale: the sale's start date and time in Japan time, and the price 税込 (tax-inclusive);
- OnSale: the price 税込 and an action to buy. When the TicketType is LowStock, the section adds 残りわずか (few left) and never shows a count;
- AllHeld: 売り切れ (sold out), with the note that other fans are checking out and that tickets may be available again in a few minutes;
- SoldOut: 売り切れ;
- Ended: that the sale has ended.

When the FirstCome TicketType is SoldOut or Ended and its resale is open, the section SHALL add, below that state, 公式リセール (official resale): when resale is available, the price 税込, that resale tickets are sold at face value, and an action to buy; when it is not, that tickets listed by fans who cannot attend can be bought here, with no action. It SHALL never show how many tickets are listed.

For a Lottery sale, the section SHALL show its start and end date and time in Japan time and the price 税込, and while its window is open an action to enter, which opens the lottery entry screen for the TicketType; outside the window it shows no action. When the Event has no sale, the section SHALL show no sale.

The action to buy or to enter SHALL open the checkout or the entry screen for a signed-in fan. For a guest, it SHALL start sign-up and return to the Event page. The fan's purchased tickets are shown as before.

#### Scenario: On sale with few left

- **WHEN** a guest opens the page of a first-come sale whose TicketType is OnSale and LowStock, priced 3000 yen
- **THEN** the section shows 3,000円（税込）, 残りわずか and the action to buy, with no count

#### Scenario: Guest buys

- **WHEN** a guest taps the action to buy
- **THEN** sign-up starts and, once it completes, the guest is back on the Event page

#### Scenario: Not yet on sale

- **WHEN** the first-come sale opens on 2026-11-01 10:00
- **THEN** the section shows the opening date and time and no action to buy

#### Scenario: Temporarily all held

- **WHEN** the first-come sale's TicketType is AllHeld
- **THEN** the section shows 売り切れ with the note that tickets may be available again in a few minutes

#### Scenario: Sold out with a resale ticket

- **WHEN** the first-come TicketType priced 5000 yen is SoldOut and resale is available
- **THEN** the section shows 売り切れ, then 公式リセール with 5,000円（税込）, the face-value note and the action to buy

#### Scenario: Sold out, nothing listed

- **WHEN** the first-come TicketType is SoldOut, its resale is open and resale is not available
- **THEN** the section shows 売り切れ and 公式リセール with the note that listed tickets can be bought here, and no action to buy

#### Scenario: Presale over, general sale upcoming

- **WHEN** a lottery presale ended on 10 November and a first-come general sale opens on 20 November, and the fan opens the page on 15 November
- **THEN** the section shows the general sale's name and its opening date and time

#### Scenario: Lottery open

- **WHEN** a lottery sale named ファンクラブ先行 is open, priced 8000 yen
- **THEN** the section shows ファンクラブ先行, its window, 8,000円（税込） and the action to enter, which opens the entry screen for the Event's TicketType

#### Scenario: Every sale ended

- **WHEN** the presale and the general sale have both ended
- **THEN** the section shows the general sale as ended

#### Scenario: No sale

- **WHEN** no sale offers the Event
- **THEN** the section shows no sale
