# Spec Delta

## Purpose

ReservationUseCase.Start begins a fan's checkout, or resumes it: it holds the chosen number of tickets for 15 minutes and returns what the fan needs to finish, including their saved 本人確認 (identity check) details.

## ADDED Requirements

### Requirement: Start a checkout while the sale is on

Start SHALL take the calling fan, a TicketSale, a count and the current time:
- It SHALL read the sale with TicketSale.Get, failing with NotFound when it does not exist.
- It SHALL fail with FailedPrecondition when Event.IsEventPublished reports false for the sale's event, as for a 中止 (cancelled) concert, or when the sale's state is not OnSale or AllHeld.
- It SHALL fail with InvalidArgument when the count is below 1 or above the sale's per-account limit.
- It SHALL then call Reservation.GetOrCreateHeld, whose failures are returned unchanged.

Starting again with the same count while the hold lasts SHALL resume the same Reservation.

#### Scenario: Fan starts a checkout

- **WHEN** a signed-in fan starts a checkout for 2 tickets on an OnSale sale
- **THEN** 2 tickets are held for 15 minutes and the Reservation is returned

#### Scenario: Fan reloads mid-checkout

- **WHEN** the fan reloads the page and starts again with the same count within the hold
- **THEN** the same Reservation is returned with its original hold expiry

#### Scenario: Sale not open yet

- **WHEN** the sale is NotYetOnSale
- **THEN** Start fails with FailedPrecondition and nothing is held

#### Scenario: Concert cancelled

- **WHEN** the event's concert was cancelled after the sale opened
- **THEN** Start fails with FailedPrecondition and nothing is held

#### Scenario: Last tickets in other checkouts

- **WHEN** the sale is AllHeld
- **THEN** Start fails with ResourceExhausted and nothing is held

### Requirement: Returns what the checkout shows

Start SHALL return the Reservation's id, count, amount and hold expiry, the sale's price, and the fan's holder full name and phone number as stored on the User, or none when the fan has not checked out before.

#### Scenario: Returning buyer

- **WHEN** a fan who checked out before starts a checkout
- **THEN** their saved name and phone number are returned for the checkout to prefill
