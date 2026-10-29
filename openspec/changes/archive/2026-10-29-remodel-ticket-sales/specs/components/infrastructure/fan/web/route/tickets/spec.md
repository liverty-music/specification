# Spec Delta

## MODIFIED Requirements

### Requirement: Tickets grouped by event with their face

The screen SHALL list the signed-in fan's tickets grouped by event, nearest event first. Each ticket SHALL show its event's title, date, venue, open and start times, its seat type's name, and its covered-ticket face: that resale without the Organizer's consent is prohibited, the eligible person's full name and phone number as the fan's User currently records them, and that no seat is assigned. Each ticket SHALL show its state: 未入場 (not yet entered), 出品中 (listed for official resale), 入場済み (entered) with the admit time, リセール済み (resold) for a ticket voided by its Sold listing, or 無効 (void) for any other voided ticket. The last loaded list SHALL stay viewable without a connection.

#### Scenario: Fan opens their tickets

- **WHEN** a fan with 3 S席 tickets for one event opens the screen
- **THEN** the event is shown once with its 3 tickets, each with S席, the resale notice, the fan's full name and phone number and 未入場

#### Scenario: Fan corrected their phone number

- **WHEN** the fan changed their phone number after the tickets were issued and opens the screen with a connection
- **THEN** each ticket's face shows the new phone number

#### Scenario: Refunded ticket

- **WHEN** one of the fan's tickets was voided by a refund
- **THEN** it is shown as 無効 and offers no QR code

#### Scenario: Resold ticket

- **WHEN** one of the fan's tickets was bought by another fan through official resale
- **THEN** it is shown as リセール済み and offers no QR code

#### Scenario: No signal in the venue

- **WHEN** the fan opens the screen without a connection after loading it earlier
- **THEN** the tickets loaded earlier are shown

### Requirement: List a ticket for official resale

The screen SHALL read the fan's listings with ResaleListingService.List and, for each event, its sales with TicketSaleService.ListByEvent. For a ticket that is 未入場 and has no Listed listing, whose TicketStock has its resale open, the screen SHALL offer to list it for 公式リセール. Before listing, it SHALL show on one screen: the price 税込, the resale fee of 10%, the refund amount, that the refund goes to the card the fan paid with right after another fan buys the ticket, that the listing closes when admission opens with that date and time, that a sale is not guaranteed and an unsold ticket stays valid, that the listing can be withdrawn until another fan starts buying it, and that a sold ticket becomes invalid. Confirming SHALL call ResaleListingService.Create for that one ticket. A ticket whose TicketStock is not sold out SHALL offer no listing, and the screen SHALL say that official resale opens only when the seat type sells out for the event.

#### Scenario: Fan lists a ticket
- **WHEN** a fan with 2 S席 tickets of 5000 yen for an event whose S席 sold out lists one of them
- **THEN** the screen shows 5,000円, 手数料 500円 and 返金額 4,500円 before confirming, and after confirming that ticket is shown as 出品中

#### Scenario: Event not sold out
- **WHEN** the seat type of the fan's tickets never sold out for the event
- **THEN** the screen offers no listing and says official resale opens only when the seat type sells out

#### Scenario: Admission opened
- **WHEN** the fan opens the screen after the event's admission window opened
- **THEN** no listing is offered

## ADDED Requirements

### Requirement: A listed ticket can be withdrawn until it is sold or listing closes

A ticket shown as 出品中 SHALL offer to withdraw the listing, which calls ResaleListingService.Withdraw; a listing can be withdrawn until it is sold or listing closes. When withdrawing fails with FailedPrecondition, the screen SHALL say that the listing can no longer be withdrawn because it was sold or listing has closed, and SHALL read the fan's listings again. A ticket shown as リセール済み SHALL show the refund amount and whether the refund has been made, with its date. A listing returned Expired SHALL leave its ticket shown as 未入場.

#### Scenario: Fan withdraws
- **WHEN** the fan withdraws a listed ticket before listing closes
- **THEN** the ticket is shown as 未入場 again

#### Scenario: Listing already closed
- **WHEN** the fan withdraws a listed ticket after it was sold or listing closed
- **THEN** the screen says the listing can no longer be withdrawn and shows the ticket as the listings read again say

#### Scenario: Refund made
- **WHEN** the fan opens the screen after their listed ticket was resold and refunded
- **THEN** the ticket is shown as リセール済み with 返金額 4,500円 and the refund date

#### Scenario: Listing expired
- **WHEN** the fan opens the screen after admission opened and their listing did not sell
- **THEN** the ticket is shown as 未入場 and its QR code can be shown

## REMOVED Requirements

### Requirement: A listed ticket can be withdrawn and shows its outcome

**Reason**: A Checkout no longer buys resale tickets (design D7), so no fan can be buying a listed ticket while its listing is open; a withdrawal is refused only once the listing was sold or listing closed, as the legal document says.
**Migration**: See "A listed ticket can be withdrawn until it is sold or listing closes".

