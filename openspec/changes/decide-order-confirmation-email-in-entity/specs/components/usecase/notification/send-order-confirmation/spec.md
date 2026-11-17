## MODIFIED Requirements

### Requirement: Confirmation email after every paid Order

SendOrderConfirmation SHALL run for each Order announced as paid, with its user and event. It SHALL read:
- the Order with Order.Get;
- the Order's user with User.Get;
- the event's concert with Concert.ListByIDs;
- the event's Organizer with Event.GetOrganizerID and Organizer.Get.

It SHALL send, with Order.SendConfirmationEmail to the user's email address and in the user's preferred language (Japanese when none), a message stating:
- for an Order whose source is a LotteryEntry, that the entry won the lottery;
- the concert's title, date, venue, and open and start times;
- the number of tickets and the total paid, 税込 (tax-inclusive);
- the pay time, the payment method (card) and the card brand and last four digits;
- the Organizer's business details: legal name, representative name, business address, business phone number and contact email;
- that resale of the tickets without the Organizer's consent is prohibited;
- that tickets cannot be cancelled or refunded except when the concert is 中止 (cancelled);
- how to show the tickets.

When reading or sending fails, SendOrderConfirmation SHALL fail with that error and is run again; it SHALL send the email only while none has been sent for the Order (Order.ConfirmationEmailDue) and then record the send (Order.MarkConfirmationSent), so a run again after the email was sent sends no second email.

#### Scenario: Checkout paid
- **WHEN** a fan's Order for 2 tickets of 6000 yen is announced as paid
- **THEN** the fan receives one email with the concert, 2 tickets, 6000 yen 税込, the card's last four digits, the Organizer's business details, the resale prohibition and the cancellation policy

#### Scenario: Lottery win
- **WHEN** the Order of a won lottery entry is announced as paid
- **THEN** the winner receives the same confirmation email for their tickets, first saying that the entry won

#### Scenario: Order announced twice
- **WHEN** the same announcement is delivered twice
- **THEN** the fan receives one email

#### Scenario: Mail unavailable
- **WHEN** Order.SendConfirmationEmail fails with Unavailable
- **THEN** SendOrderConfirmation fails and the email is sent when it runs again
