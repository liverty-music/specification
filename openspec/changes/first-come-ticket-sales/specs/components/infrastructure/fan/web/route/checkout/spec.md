# Spec Delta

## Purpose

The fan's checkout screens for a first-come ticket sale: choosing how many tickets, confirming the 本人確認 (identity check) details, paying by card, and the 特商法 (Specified Commercial Transactions Act) final confirmation before the order is placed, ending on a completion screen.

## ADDED Requirements

### Requirement: Choose the count and hold the tickets

The checkout SHALL open from an event's ticket section for a signed-in fan. It SHALL offer a count from 1 to the sale's per-account limit, showing the price per ticket and the total, both 税込 (tax-inclusive). Continuing SHALL hold the tickets with ReservationUseCase.Start and show how long the hold lasts, counting down from its expiry. When continuing fails with FailedPrecondition, the checkout SHALL re-read the sale with TicketSaleUseCase.Get and say the sale has ended, sold out or was cancelled when it is no longer OnSale or AllHeld, and that the per-account limit was reached otherwise. While a request is in flight, the continue action SHALL be disabled. Reopening the checkout during the hold SHALL resume it with the same countdown.

#### Scenario: Fan picks two tickets

- **WHEN** a fan picks 2 tickets of 3000 yen
- **THEN** the total shows 6,000円（税込） and continuing holds them with a 15-minute countdown

#### Scenario: Fan reloads mid-checkout

- **WHEN** the fan reloads the page 5 minutes into the hold
- **THEN** the checkout resumes with 10 minutes left

#### Scenario: Last tickets in other checkouts

- **WHEN** continuing fails because the remaining tickets are held by others
- **THEN** the screen says the tickets are sold out for now, that other fans are checking out, and that they may be available again in a few minutes

#### Scenario: Over the limit

- **WHEN** continuing fails because the fan would exceed the per-account limit
- **THEN** the screen says how many tickets one account may buy

#### Scenario: Sale ended before continuing

- **WHEN** continuing fails because the sale ended or sold out after the fan opened the checkout
- **THEN** the screen re-reads the sale and says it has ended or sold out, not that the limit was reached

### Requirement: Identity details, prefilled

The checkout SHALL ask for the 本人確認 full name and phone number, prefilled with the fan's saved details. The phone number field SHALL accept a Japanese domestic number or an E.164 number, with or without separators, and send it in E.164 form, as the lottery application screen does. It SHALL state that the name is printed on the tickets and checked at entry.

#### Scenario: Returning buyer

- **WHEN** a fan who bought before reaches the identity step
- **THEN** their name and phone number are already filled in and can be edited

### Requirement: Card payment

The checkout SHALL take the card through a card form that also offers Apple Pay or Google Pay where the device supports them. It SHALL authorize the card with ReservationUseCase.Authorize and complete the card issuer's authentication in the page. It SHALL say that the card is not charged until the order is placed.

#### Scenario: Card declined

- **WHEN** the card issuer declines the authentication
- **THEN** the screen says the card could not be used and lets the fan try another card without losing the hold

#### Scenario: Hold ended before authorizing

- **WHEN** authorizing fails because the hold has ended
- **THEN** the screen says the 15 minutes have passed and offers to start again

### Requirement: 特商法 final confirmation

Before placing the order, the checkout SHALL show on one screen:
- the event, its date, venue, and open and start times;
- the number of tickets, with the price per ticket and the total to pay, 税込;
- the payment method, credit card, with the card brand and last four digits, and that the card is charged when the order is placed;
- that the tickets are available in the app's Tickets screen immediately after purchase;
- the sale period;
- that resale of the tickets without the organizer's consent is prohibited, and that the tickets are issued to the buyer's name;
- that the purchase cannot be cancelled or refunded except when the event is 中止 (cancelled), that no cooling-off applies, and that official resale opens only if the event sells out;
- the Organizer's seller details, as returned by TicketSaleUseCase.Get: legal name, representative, address, phone number and contact email.

It SHALL offer to go back and change the number of tickets or the identity details from this screen. The place-order action SHALL state that it pays, with the amount, and SHALL be disabled while the order is being placed.

#### Scenario: Final confirmation shown

- **WHEN** a fan reaches the last step for 2 tickets of 3000 yen
- **THEN** every listed item is shown and the action reads 6,000円を支払って購入する

#### Scenario: Fan corrects the name

- **WHEN** the fan goes back from the final confirmation to change their name and returns
- **THEN** the final confirmation shows the corrected name and the same hold

#### Scenario: Double tap on the action

- **WHEN** the fan taps the action twice
- **THEN** the order is placed once

### Requirement: Outcome of placing the order

Placing the order SHALL call IssuanceUseCase.IssueFromReservation. On success, the checkout SHALL show the completion screen with the event, the number of tickets, the total paid and a link to the Tickets screen. It SHALL then offer to allow notifications when the fan has not allowed them, and to add the app to the home screen when it is not installed. On failure, it SHALL read the checkout with ReservationUseCase.Get and say:
- when the hold has ended without a commit: that the 15 minutes passed, that the card was not charged, that a temporary hold may show on the card statement for a few days, and offer to start again;
- when the checkout was released after being committed: that the card could not be charged, and offer to start again;
- when the checkout was released without being committed: that it was replaced by a newer checkout, for example in another tab, and offer to go to it;
- when the card authentication is not complete: to finish it and try again;
- otherwise: that the purchase is being completed and the tickets will appear in the Tickets screen shortly.

#### Scenario: Purchase placed

- **WHEN** the purchase succeeds
- **THEN** the completion screen shows 2 tickets and 6,000円 with a link to the Tickets screen

#### Scenario: Hold ended at the last step

- **WHEN** placing the order fails because the hold has ended
- **THEN** the screen says the 15 minutes passed and the card was not charged, and offers to start again

#### Scenario: Charge still completing

- **WHEN** placing the order fails with Unavailable after the commit
- **THEN** the screen says the purchase is being completed and the tickets will appear shortly
