## MODIFIED Requirements

### Requirement: List a ticket for official resale

The screen SHALL read the fan's listings with ResaleListingService.List and, for each event, its sales with TicketSaleService.ListByEvent. For a ticket that is 未入場 and has no Listed listing, whose TicketStock has its resale open, the screen SHALL offer to list it for 公式リセール. Before listing, it SHALL show on one screen: the price 税込, the resale fee of 10%, the refund amount, that the refund goes to the card the fan paid with right after another fan buys the ticket, that the listing closes at the resale deadline (12:00 at the venue's local time on the event's day or 3 hours before the start time, whichever is earlier) with that date and time shown as global/i18n "Each kind of time is shown in the zone it belongs to" states for a resale deadline, that a sale is not guaranteed and an unsold ticket stays valid, that the listing can be withdrawn until a draw allocates it or listing closes, and that a sold ticket becomes invalid. Confirming SHALL call ResaleListingService.Create for that one ticket. A ticket whose TicketStock is not sold out SHALL offer no listing, and the screen SHALL say that official resale opens only when the seat type sells out for the event.

#### Scenario: Fan lists a ticket
- **WHEN** a fan with 2 S席 tickets of 5000 yen for an event whose S席 sold out lists one of them
- **THEN** the screen shows 5,000円, 手数料 500円 and 返金額 4,500円 before confirming, and after confirming that ticket is shown as 出品中

#### Scenario: Resale deadline of an event abroad
- **WHEN** a fan whose browser is set to Japan time opens the listing of a ticket for an event at a Venue in London on 2027-02-20 that starts at 19:30
- **THEN** the screen says listing closes at 2月20日(土) 12:00 ロンドン時間（日本時間 21:00）

#### Scenario: Event not sold out
- **WHEN** the seat type of the fan's tickets never sold out for the event
- **THEN** the screen offers no listing and says official resale opens only when the seat type sells out

#### Scenario: Admission opened
- **WHEN** the fan opens the screen after the event's admission window opened
- **THEN** no listing is offered
