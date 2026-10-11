# components/usecase/order/fulfill-payment Specification

## Purpose
IssuanceUseCase.FulfillPayment turns a completed charge reported by the payment provider into a paid Order and announces it, so every paid Order's confirmation and ticket journey update run, whether the charge came from a checkout or a won lottery.

## Requirements

### Requirement: Each completed charge ends in an announced Order

FulfillPayment SHALL take the reference of a completed charge and find its source:
- a Reservation with Reservation.GetByAuthorizationRef, for which it SHALL run IssuanceUseCase.IssueFromReservation without a calling fan;
- otherwise a TicketApplication with TicketApplication.GetByPaymentIntentRef, for which it SHALL run IssuanceUseCase.IssueFromCapturedWin.

It SHALL then announce that the Order is paid, carrying the Order, its buyer, its event, its number of Tickets, its amount and its source. The announcement SHALL be deduplicated by the Order, so announcing the same Order again does not reach a consumer twice within the deduplication window, and consumers SHALL treat a repeated announcement of an Order as one.

When neither source has the reference, FulfillPayment SHALL succeed without effect. When issuing or announcing fails, FulfillPayment SHALL fail with that error, so the provider reports the charge again.

#### Scenario: Checkout charged

- **WHEN** the charge of a fan's checkout completes
- **THEN** the checkout's Order is issued, or found when it already was, and announced as paid

#### Scenario: Lottery win charged

- **WHEN** the charge of a won lottery application completes
- **THEN** the application's Order is issued, or found, and announced as paid

#### Scenario: Charge reported twice

- **WHEN** the same completed charge is reported twice
- **THEN** one Order exists and its announcement reaches each consumer once

#### Scenario: Messaging unavailable

- **WHEN** announcing the Order fails
- **THEN** FulfillPayment fails, and the Order is announced when the charge is reported again

#### Scenario: Charge of another system

- **WHEN** the charge belongs to no Reservation and no TicketApplication
- **THEN** FulfillPayment succeeds and nothing changes
