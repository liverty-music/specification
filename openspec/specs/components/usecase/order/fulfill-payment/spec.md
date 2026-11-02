# components/usecase/order/fulfill-payment Specification

## Purpose
OrderUseCase.FulfillPayment turns a completed charge reported by the payment provider into a paid Order through Order.Issue, which announces the Order as paid, so every paid Order's confirmation and ticket journey update run, whether the charge came from a checkout or a won lottery entry.

## Requirements

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
