# Spec Delta

## Purpose

NotificationUseCase.NotifyTicketPurchased tells a buyer their purchase went through, whether from a checkout or a won lottery: an email with the purchase details and the seller's disclosure, and a push notification that opens their tickets.

## ADDED Requirements

### Requirement: Confirmation email after every recorded purchase

NotifyTicketPurchased SHALL run for each announced TicketPurchased, with its Order, buyer and event. It SHALL read:
- the Order with Order.Get;
- the buyer with User.Get;
- the event's concert with Concert.ListByIDs;
- the event's Organizer with Event.GetOrganizerID and Organizer.Get.

It SHALL send, with Order.SendConfirmationEmail to the buyer's email address and in the buyer's preferred language (Japanese when none), a message stating:
- the concert's title, date, venue, and open and start times;
- the number of tickets and the total paid, 税込 (tax-inclusive);
- the paid time, the payment method (card) and the card brand and last four digits;
- the Organizer's seller details;
- that resale of the tickets without the organizer's consent is prohibited;
- that tickets cannot be cancelled or refunded except when the concert is 中止 (cancelled);
- how to show the tickets.

When reading or sending fails, NotifyTicketPurchased SHALL fail with that error and is run again; Order.SendConfirmationEmail keeps it to one email per Order.

#### Scenario: Checkout paid

- **WHEN** the purchase of a fan's 2 tickets for 6000 yen is announced
- **THEN** the fan receives one email with the concert, 2 tickets, 6000 yen 税込, the card's last four digits, the Organizer's seller details, the resale prohibition and the cancellation policy

#### Scenario: Lottery win

- **WHEN** the purchase of a won lottery application is announced
- **THEN** the winner receives the same confirmation email for their tickets

#### Scenario: Purchase announced twice

- **WHEN** the same TicketPurchased is delivered twice
- **THEN** the fan receives one email

#### Scenario: Mail unavailable

- **WHEN** Order.SendConfirmationEmail fails with Unavailable
- **THEN** NotifyTicketPurchased fails and the email is sent when it runs again

### Requirement: Push notification after the email

After the email is sent, NotifyTicketPurchased SHALL request a notification of type ticket_purchased for the buyer with NotificationUseCase.Deliver, saying the purchase is complete in the buyer's language and opening the Tickets screen when tapped. A buyer with no registered browser receives the email only. If NotifyTicketPurchased stops between requesting the notification and finishing, a run again can push a second notification; the email is still sent once.

#### Scenario: Fan allowed notifications

- **WHEN** the buyer has a registered browser
- **THEN** a ticket_purchased notification is pushed and opens the Tickets screen
