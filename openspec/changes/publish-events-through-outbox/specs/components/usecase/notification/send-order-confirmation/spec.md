## MODIFIED Requirements

### Requirement: Push notification after the email

After the email is sent, SendOrderConfirmation SHALL start NotificationUseCase.Deliver for the Order's user with a notification of type order_confirmation, named after the type and the Order, saying the purchase is complete in the user's language and opening the Tickets screen when tapped. A user with no registered browser receives the email only. A run again for the same Order, after a stop or a repeated announcement, starts no second Deliver, so the fan is pushed once; the email is still sent once.

#### Scenario: Fan allowed notifications

- **WHEN** the Order's user has a registered browser
- **THEN** an order_confirmation notification is pushed and opens the Tickets screen

#### Scenario: Paid announcement delivered twice

- **WHEN** the paid announcement of an Order is delivered twice and SendOrderConfirmation runs twice
- **THEN** the fan receives one email and one order_confirmation push
