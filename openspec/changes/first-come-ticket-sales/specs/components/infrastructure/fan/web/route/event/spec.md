# Spec Delta

## ADDED Requirements

### Requirement: Ticket section shows the sale

When the Event has a TicketSale, read with TicketSaleUseCase.Get, the ticket section SHALL show, by the sale's state:
- NotYetOnSale: the sale start date and time in Japan time, and the price 税込 (tax-inclusive);
- OnSale: the price 税込 and an action to buy. When the sale is LowStock, the section adds 残りわずか (few left) and never shows a count;
- AllHeld: 売り切れ (sold out), with the note that other fans are checking out and that tickets may be available again in a few minutes;
- SoldOut: 売り切れ;
- Ended: that the sale has ended.

The action to buy SHALL open the checkout for a signed-in fan. For a guest, it SHALL start sign-up and return to the Event page. The fan's purchased tickets are shown as before.

#### Scenario: On sale with few left

- **WHEN** a guest opens the page of an OnSale, LowStock sale priced 3000 yen
- **THEN** the section shows 3,000円（税込）, 残りわずか and the action to buy, with no count

#### Scenario: Guest buys

- **WHEN** a guest taps the action to buy
- **THEN** sign-up starts and, once it completes, the guest is back on the Event page

#### Scenario: Not yet on sale

- **WHEN** the sale opens on 2026-11-01 10:00
- **THEN** the section shows the opening date and time and no action to buy

#### Scenario: Temporarily all held

- **WHEN** the sale is AllHeld
- **THEN** the section shows 売り切れ with the note that tickets may be available again in a few minutes
