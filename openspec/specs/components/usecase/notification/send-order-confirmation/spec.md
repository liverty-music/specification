# components/usecase/notification/send-order-confirmation Specification

## Purpose
NotificationUseCase.SendOrderConfirmation tells a buyer their purchase went through, whether from a checkout or a won lottery: an email with the purchase details and the seller's disclosure, and a push notification that opens their tickets.

## Requirements

### Requirement: Confirmation email after every paid Order

SendOrderConfirmation SHALL run for each Order announced as paid, with its buyer and event. It SHALL read:
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

When reading or sending fails, SendOrderConfirmation SHALL fail with that error and is run again; Order.SendConfirmationEmail keeps it to one email per Order.

#### Scenario: Checkout paid

- **WHEN** a fan's Order for 2 tickets of 6000 yen is announced as paid
- **THEN** the fan receives one email with the concert, 2 tickets, 6000 yen 税込, the card's last four digits, the Organizer's seller details, the resale prohibition and the cancellation policy

#### Scenario: Lottery win

- **WHEN** the Order of a won lottery application is announced as paid
- **THEN** the winner receives the same confirmation email for their tickets

#### Scenario: Order announced twice

- **WHEN** the same announcement is delivered twice
- **THEN** the fan receives one email

#### Scenario: Mail unavailable

- **WHEN** Order.SendConfirmationEmail fails with Unavailable
- **THEN** SendOrderConfirmation fails and the email is sent when it runs again

### Requirement: Push notification after the email

After the email is sent, SendOrderConfirmation SHALL request a notification of type order_confirmation for the buyer with NotificationUseCase.Deliver, saying the purchase is complete in the buyer's language and opening the Tickets screen when tapped. A buyer with no registered browser receives the email only. If SendOrderConfirmation stops between requesting the notification and finishing, a run again can push a second notification; the email is still sent once.

#### Scenario: Fan allowed notifications

- **WHEN** the buyer has a registered browser
- **THEN** an order_confirmation notification is pushed and opens the Tickets screen
