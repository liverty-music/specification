## MODIFIED Requirements

### Requirement: Each completed charge ends in an announced Order

FulfillPayment SHALL take the card authorization of a completed charge and find its source:
- a Checkout with Checkout.GetByCardAuthorizationID, for which it SHALL run OrderUseCase.IssueFromCheckout without a calling fan and then announce that the Order is paid, carrying the Order, its user, its event, its number of Tickets, its amount and its source;
- otherwise a LotteryEntry with LotteryEntry.GetByCardAuthorizationID, for which it SHALL succeed without effect, because OrderUseCase.Issue charged the entry's Order and announced it.

Each announcement is a new message, so a charge reported again announces the Order again; consumers that act on the Order SHALL treat a repeated announcement of an Order as one. The order-paid signal for product analytics is keyed by the announcement, so a charge reported again records a second order-paid signal for the same Order.

When neither source has the card authorization, FulfillPayment SHALL succeed without effect. When issuing or announcing fails, FulfillPayment SHALL fail with that error, so the provider reports the charge again.

#### Scenario: Checkout charged

- **WHEN** the charge of a fan's checkout completes
- **THEN** the checkout's Order is issued, or found when it already was, and announced as paid

#### Scenario: Lottery win charged

- **WHEN** the charge of a won lottery entry completes
- **THEN** FulfillPayment succeeds, nothing changes, and the Order stays announced once, by OrderUseCase.Issue

#### Scenario: Charge reported twice

- **WHEN** the same completed charge of a checkout is reported twice
- **THEN** one Paid Order exists, it is announced twice, each consumer that acts on the Order acts on it once, and product analytics records two order-paid signals for that Order

#### Scenario: Messaging unavailable

- **WHEN** announcing the Order of a checkout fails
- **THEN** FulfillPayment fails, and the Order is announced when the charge is reported again

#### Scenario: Charge of another system

- **WHEN** the charge belongs to no Checkout and no LotteryEntry
- **THEN** FulfillPayment succeeds and nothing changes
