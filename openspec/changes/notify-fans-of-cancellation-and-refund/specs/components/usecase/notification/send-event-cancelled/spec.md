## Purpose

NotificationUseCase.SendEventCancelled tells each fan who bought tickets for an Event that it is 中止 (cancelled) and that the price of the tickets they still hold is refunded: an email, and a push notification that opens the event's page.

## ADDED Requirements

### Requirement: Every buyer of a cancelled event is told once per order

SendEventCancelled SHALL run for each Event announced as cancelled by Series.CancelEvents. It SHALL list the Event's Orders with Order.ListByEvent and run the notice of the next requirement for each Paid Order, once per Order: a run again for the same Event, after a stop or a repeated announcement, sends no second email and no second push for an Order already told. A Refunded Order SHALL NOT be told of the cancellation; its refund notice says the concert was cancelled. When listing fails, SendEventCancelled SHALL fail with that error and run again; a failure for one Order SHALL NOT stop the notices of the Event's other Orders.

#### Scenario: Two buyers
- **WHEN** an Event with two Paid Orders of two fans is announced as cancelled
- **THEN** each of the two fans receives one email and one event_cancelled push

#### Scenario: Already refunded
- **WHEN** an Event is announced as cancelled and one of its Orders is already Refunded
- **THEN** that Order's fan receives no cancellation notice

#### Scenario: Cancellation announced twice
- **WHEN** the same announcement is delivered twice
- **THEN** each fan receives one email and one push per Order

#### Scenario: No buyer
- **WHEN** an Event with no Paid Order is announced as cancelled
- **THEN** nothing is sent

### Requirement: The cancellation notice

For one Paid Order, SendEventCancelled SHALL read:
- the Order with Order.Get, its user with User.Get and its event with Order.GetEventID;
- the event's concert with Concert.ListByIDs;
- the user's Tickets of that event with Ticket.ListByUserAndEvent, counting the Order's Issued Tickets.

It SHALL send, with Order.SendCancellationEmail to the user's email address and in the user's preferred language (Japanese when none), a message stating:
- the concert's title, date and venue, and that it is 中止 (cancelled);
- the number of the Order's Issued Tickets and their price, 税込 (tax-inclusive): the Order's amount divided by its ticket count, times that number;
- that this price is refunded to the card with the Order's card brand and last four digits, and that a second notice follows once the refund is made;
- when the Order has a Ticket resold through official resale (公式リセール), that the resold Ticket was already refunded at its sale.

After the email is sent, it SHALL start NotificationUseCase.Deliver for the user with a notification of type event_cancelled, named after the type and the Order, saying in the user's language that the concert is cancelled and its tickets are refunded, and opening the event's page when tapped. A user with no registered browser receives the email only. When the Order is no longer Paid or no longer exists when it is read, SendEventCancelled SHALL send nothing for it. When reading or sending fails otherwise, that Order's notice SHALL fail and run again.

#### Scenario: Cancellation email
- **WHEN** the notice runs for a Paid 6000 yen Order of 2 Issued Tickets paid with a VISA card ending in 1234
- **THEN** the fan receives one email with the concert, that it is cancelled, 2 tickets, 6000 yen 税込 and the card VISA ending in 1234

#### Scenario: One ticket resold
- **WHEN** the notice runs for a 6000 yen Order of 2 Tickets, one of them resold
- **THEN** the email states 1 ticket and 3000 yen, and that the resold ticket was already refunded

#### Scenario: Fan allowed notifications
- **WHEN** the Order's user has a registered browser
- **THEN** an event_cancelled notification is pushed and opens the event's page

#### Scenario: Refunded before the notice
- **WHEN** the Order became Refunded before its notice read it
- **THEN** nothing is sent for that Order

#### Scenario: Event deleted before the notice
- **WHEN** Order.Get fails with NotFound because the Event was deleted with its Orders
- **THEN** nothing is sent for that Order and its notice is finished

#### Scenario: Mail unavailable
- **WHEN** Order.SendCancellationEmail fails with Unavailable
- **THEN** that Order's notice fails and the email is sent when it runs again
