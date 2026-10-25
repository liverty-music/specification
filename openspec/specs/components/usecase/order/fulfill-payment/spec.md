# components/usecase/order/fulfill-payment Specification

## Purpose
OrderUseCase.FulfillPayment turns a completed charge reported by the payment provider into a paid Order and announces it, so every paid Order's confirmation and ticket journey update run, whether the charge came from a checkout or a won lottery entry.

## Requirements

### Requirement: Each completed charge ends in an announced Order

FulfillPayment SHALL take the card authorization of a completed charge and find its source:
- a Checkout with Checkout.GetByCardAuthorizationID, for which it SHALL run OrderUseCase.IssueFromCheckout without a calling fan;
- otherwise a LotteryEntry with LotteryEntry.GetByCardAuthorizationID, for which it SHALL run OrderUseCase.IssueFromCapturedWin.

It SHALL then announce that the Order is paid, carrying the Order, its user, its event, its number of Tickets, its amount and its source. Each announcement is a new message, so a charge reported again announces the Order again; consumers that act on the Order SHALL treat a repeated announcement of an Order as one. The order-paid signal for product analytics is keyed by the announcement, so a charge reported again records a second order-paid signal for the same Order.

When neither source has the card authorization, FulfillPayment SHALL succeed without effect. When issuing or announcing fails, FulfillPayment SHALL fail with that error, so the provider reports the charge again.

#### Scenario: Checkout charged

- **WHEN** the charge of a fan's checkout completes
- **THEN** the checkout's Order is issued, or found when it already was, and announced as paid

#### Scenario: Lottery win charged

- **WHEN** the charge of a won lottery entry completes
- **THEN** the entry's Order is issued, or found, and announced as paid

#### Scenario: Charge reported twice

- **WHEN** the same completed charge is reported twice
- **THEN** one Order exists, it is announced twice, each consumer that acts on the Order acts on it once, and product analytics records two order-paid signals for that Order

#### Scenario: Messaging unavailable

- **WHEN** announcing the Order fails
- **THEN** FulfillPayment fails, and the Order is announced when the charge is reported again

#### Scenario: Charge of another system

- **WHEN** the charge belongs to no Checkout and no LotteryEntry
- **THEN** FulfillPayment succeeds and nothing changes

### Requirement: A paid order is reported for product analytics

When FulfillPayment announces an Order as paid, an "order paid" signal for product analytics SHALL be sent for the fan, carrying the Order, its Event, the ticket count, the amount and currency, whether the Order came from a won LotteryEntry or a Checkout, and the Order's pay time as the time it happened. A redelivery of the same announcement SHALL be recorded once; a second announcement of the same Order is recorded again (see "Each completed charge ends in an announced Order"). A failure to send it SHALL NOT fail or undo the payment.

#### Scenario: Paid checkout
- **WHEN** a fan's Checkout for 2 tickets is paid
- **THEN** one order-paid signal is sent with ticket count 2, the amount, the currency and the source Checkout

#### Scenario: Announcement handled twice
- **WHEN** the same paid announcement of one Order is delivered twice
- **THEN** one order-paid signal is recorded for that Order, at its pay time
