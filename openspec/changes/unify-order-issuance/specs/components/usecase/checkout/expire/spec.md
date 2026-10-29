## Purpose

CheckoutUseCase.Expire ends a fan's hold when its 15 minutes pass, so its tickets are on sale again and its Order is Void.

## ADDED Requirements

### Requirement: Every hold ends at its expiry

Expire SHALL run once for each Held Checkout that Checkout.GetOrCreateHeld creates. It SHALL wait until the Checkout's hold expiry, also across a stop of the process, and then call Checkout.Release with that time, which makes a Checkout still Held Expired and its Order Void and leaves a Checkout committed, replaced or already ended unchanged. When Release fails with Unavailable it SHALL try again.

#### Scenario: Fan walked away
- **WHEN** a fan's hold expires at 18:15 while the Checkout is still Held
- **THEN** at 18:15 the Checkout is Expired, its Order is Void and its tickets are on sale again

#### Scenario: Committed before the expiry
- **WHEN** the Checkout is committed at 18:14
- **THEN** Expire changes nothing at 18:15 and the Order stays Pending

#### Scenario: Process stopped while waiting
- **WHEN** the process stops at 18:05 and starts again at 18:20
- **THEN** Expire ends the hold right after the start, and only once
