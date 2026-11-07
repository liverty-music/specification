## MODIFIED Requirements

### Requirement: Push notification after the email

After the email is sent, for an Order whose source is a LotteryEntry, SendOrderConfirmation SHALL start NotificationUseCase.Deliver for the Order's user with a notification of type lottery_win whose subject is the Order, named after the type and the Order; tapped, it opens the Tickets screen. An Order paid at checkout SHALL NOT be pushed: the fan has just completed the purchase on screen, and the email confirms it. A user with no registered browser receives the email only. A run again for the same Order, after a stop or a repeated announcement, starts no second Deliver, so the fan is pushed once; the email is still sent once.

#### Scenario: Fan allowed notifications

- **WHEN** an Order paid at checkout is announced as paid and its user has a registered browser
- **THEN** the fan receives the email and no push

#### Scenario: Lottery winner allowed notifications

- **WHEN** the Order of a won lottery entry is announced as paid and its user has a registered browser
- **THEN** a lottery_win notification is pushed and opens the Tickets screen

#### Scenario: Paid announcement delivered twice

- **WHEN** the paid announcement of a won lottery entry's Order is delivered twice and SendOrderConfirmation runs twice
- **THEN** the fan receives one email and one lottery_win push
