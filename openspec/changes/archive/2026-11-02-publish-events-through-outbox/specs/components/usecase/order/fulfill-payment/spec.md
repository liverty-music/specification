## REMOVED Requirements

### Requirement: Each completed charge ends in an announced Order
**Reason**: FulfillPayment no longer announces: Order.Issue announces every issued Order once (components/entity/order/issue). Replaced by "Each completed charge ends in an issued Order".
**Migration**: A charge reported again finds the Order Paid and announces nothing.

### Requirement: A paid order is reported for product analytics
**Reason**: The paid announcement is made by Order.Issue, for every issued Order once (components/entity/order/issue, "An issued Order is announced as paid"), so the signal no longer depends on FulfillPayment and a repeated charge notice records nothing.
**Migration**: Product analytics records the "order paid" signal from Order.Issue's announcement, with the same content: the Order, its Event, the ticket count, the amount and currency, the source and the pay time.

## ADDED Requirements

### Requirement: Each completed charge ends in an issued Order

FulfillPayment SHALL take the card authorization of a completed charge and find its source:
- a Checkout with Checkout.GetByCardAuthorizationID, for which it SHALL run OrderUseCase.IssueFromCheckout without a calling fan;
- otherwise a LotteryEntry with LotteryEntry.GetByCardAuthorizationID, for which it SHALL run OrderUseCase.IssueFromCapturedWin.

A charge reported again finds the Order already Paid and SHALL succeed without effect. When neither source has the card authorization, FulfillPayment SHALL succeed without effect. When issuing fails, FulfillPayment SHALL fail with that error, so the provider reports the charge again.

#### Scenario: Checkout charged

- **WHEN** the charge of a fan's checkout completes and its Order is still Pending
- **THEN** the checkout's Order is issued, and so announced as paid

#### Scenario: Lottery win charged

- **WHEN** the charge of a won lottery entry completes and its Order is still Pending
- **THEN** the entry's Order is issued, and so announced as paid

#### Scenario: Charge reported twice

- **WHEN** the same completed charge is reported twice
- **THEN** one Order exists, it is announced as paid once, and product analytics records one order-paid signal for it

#### Scenario: Issuing fails

- **WHEN** issuing the Order fails with Unavailable
- **THEN** FulfillPayment fails with Unavailable, and the Order is issued when the charge is reported again

#### Scenario: Charge of another system

- **WHEN** the charge belongs to no Checkout and no LotteryEntry
- **THEN** FulfillPayment succeeds and nothing changes
