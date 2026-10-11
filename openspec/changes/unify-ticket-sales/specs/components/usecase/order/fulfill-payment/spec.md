# Spec Delta

## MODIFIED Requirements

### Requirement: Each completed charge ends in an announced Order

FulfillPayment SHALL take the reference of a completed charge and find its source:
- a Checkout with Checkout.GetByAuthorizationRef, for which it SHALL run IssuanceUseCase.IssueFromCheckout without a calling fan;
- otherwise a LotteryEntry with LotteryEntry.GetByPaymentIntentRef, for which it SHALL run IssuanceUseCase.IssueFromCapturedWin.

It SHALL then announce that the Order is paid, carrying the Order, its user, its event, its number of Tickets, its amount and its source. The announcement SHALL be deduplicated by the Order, so announcing the same Order again does not reach a consumer twice within the deduplication window, and consumers SHALL treat a repeated announcement of an Order as one.

When neither source has the reference, FulfillPayment SHALL succeed without effect. When issuing or announcing fails, FulfillPayment SHALL fail with that error, so the provider reports the charge again.

#### Scenario: Checkout charged

- **WHEN** the charge of a fan's checkout completes
- **THEN** the checkout's Order is issued, or found when it already was, and announced as paid

#### Scenario: Lottery win charged

- **WHEN** the charge of a won lottery entry completes
- **THEN** the entry's Order is issued, or found, and announced as paid

#### Scenario: Charge reported twice

- **WHEN** the same completed charge is reported twice
- **THEN** one Order exists and its announcement reaches each consumer once

#### Scenario: Messaging unavailable

- **WHEN** announcing the Order fails
- **THEN** FulfillPayment fails, and the Order is announced when the charge is reported again

#### Scenario: Charge of another system

- **WHEN** the charge belongs to no Checkout and no LotteryEntry
- **THEN** FulfillPayment succeeds and nothing changes
