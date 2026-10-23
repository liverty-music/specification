## ADDED Requirements

### Requirement: A paid order is reported for product analytics

When FulfillPayment announces an Order as paid, an "order paid" signal for product analytics SHALL be sent for the fan, carrying the Order, its Event, the ticket count, the amount and currency, and whether the Order came from a won LotteryEntry or a Checkout. The signal SHALL be sent once per paid Order, also when the announcement is handled more than once. A failure to send it SHALL NOT fail or undo the payment.

#### Scenario: Paid checkout
- **WHEN** a fan's Checkout for 2 tickets is paid
- **THEN** one order-paid signal is sent with ticket count 2, the amount, the currency and the source Checkout

#### Scenario: Announcement handled twice
- **WHEN** the paid announcement of one Order is handled twice
- **THEN** one order-paid signal is recorded for that Order
