# Spec Delta

## RENAMED Requirements

- FROM: `### Requirement: A listed ticket can be withdrawn until it is sold or listing closes`
- TO: `### Requirement: A listed ticket can be withdrawn until a draw allocates it or listing closes`

## MODIFIED Requirements

### Requirement: List a ticket for official resale

The screen SHALL read the fan's listings with ResaleListingService.List and, for each event, its sales with TicketSaleService.ListByEvent. For a ticket that is 未入場 and has no Listed listing, whose TicketStock has its resale open, the screen SHALL offer to list it for 公式リセール. Before listing, it SHALL show on one screen: the price 税込, the resale fee of 10%, the refund amount, that the refund goes to the card the fan paid with right after another fan buys the ticket, that the listing closes at the resale deadline (12:00 Japan time on the event's day or 3 hours before the start time, whichever is earlier) with that date and time, that a sale is not guaranteed and an unsold ticket stays valid, that the listing can be withdrawn until a draw allocates it or listing closes, and that a sold ticket becomes invalid. Confirming SHALL call ResaleListingService.Create for that one ticket. A ticket whose TicketStock is not sold out SHALL offer no listing, and the screen SHALL say that official resale opens only when the seat type sells out for the event.

#### Scenario: Fan lists a ticket
- **WHEN** a fan with 2 S席 tickets of 5000 yen for an event whose S席 sold out lists one of them
- **THEN** the screen shows 5,000円, 手数料 500円 and 返金額 4,500円 before confirming, and after confirming that ticket is shown as 出品中

#### Scenario: Event not sold out
- **WHEN** the seat type of the fan's tickets never sold out for the event
- **THEN** the screen offers no listing and says official resale opens only when the seat type sells out

#### Scenario: Admission opened
- **WHEN** the fan opens the screen after the event's admission window opened
- **THEN** no listing is offered

### Requirement: A listed ticket can be withdrawn until a draw allocates it or listing closes

A ticket shown as 出品中 SHALL offer to withdraw the listing, which calls ResaleListingService.Withdraw; a listing can be withdrawn until a draw allocates it or listing closes. When withdrawing fails with FailedPrecondition, the screen SHALL say that the listing can no longer be withdrawn because a draw allocated it or listing has closed, and SHALL read the fan's listings again. A ticket shown as リセール済み SHALL show the refund amount and whether the refund has been made, with its date. A listing returned Expired SHALL leave its ticket shown as 未入場.

#### Scenario: Fan withdraws
- **WHEN** the fan withdraws a listed ticket before listing closes
- **THEN** the ticket is shown as 未入場 again

#### Scenario: Listing already closed
- **WHEN** the fan withdraws a listed ticket after a draw allocated it or listing closed
- **THEN** the screen says the listing can no longer be withdrawn and shows the ticket as the listings read again say

#### Scenario: Refund made
- **WHEN** the fan opens the screen after their listed ticket was resold and refunded
- **THEN** the ticket is shown as リセール済み with 返金額 4,500円 and the refund date

#### Scenario: Listing expired
- **WHEN** the fan opens the screen after admission opened and their listing did not sell
- **THEN** the ticket is shown as 未入場 and its QR code can be shown
