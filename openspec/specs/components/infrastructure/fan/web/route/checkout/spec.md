# components/infrastructure/fan/web/route/checkout Specification

## Purpose
The fan's checkout screens for a first-come ticket sale: choosing how many tickets, confirming the 本人確認 (identity check) details, paying by card, and the 特商法 (Specified Commercial Transactions Act) final confirmation before the order is placed, ending on a completion screen.

## Requirements

### Requirement: Choose the count and hold the tickets

The checkout SHALL open from an event's ticket section for a signed-in fan, on the TicketType of the event's FirstCome sale. It SHALL offer a count from 1 to the TicketType's per-account limit, showing the price per ticket and the total, both 税込 (tax-inclusive). Continuing SHALL hold the tickets with CheckoutUseCase.Start and show how long the hold lasts, counting down from its expiry. When continuing fails with FailedPrecondition, the checkout SHALL re-read the event's sales with TicketSaleUseCase.ListByEvent and say the sale has ended, sold out or was cancelled when the TicketType is no longer OnSale or AllHeld, and that the per-account limit was reached otherwise. While a request is in flight, the continue action SHALL be disabled. Reopening the checkout during the hold SHALL resume it with the same countdown.

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
- **THEN** the screen says how many tickets one account may hold for the event, counting the tickets it already holds

#### Scenario: Sale ended before continuing

- **WHEN** continuing fails because the sale ended or sold out after the fan opened the checkout
- **THEN** the screen re-reads the sale and says it has ended or sold out, not that the limit was reached

### Requirement: Card payment

The checkout SHALL take the card through a card form that also offers Apple Pay or Google Pay where the device supports them. It SHALL authorize the card with CheckoutUseCase.AuthorizeCard, sending the full name and phone number, and complete the card issuer's authentication in the page. It SHALL say that the card is not charged until the order is placed.

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
- that resale of the tickets without the Organizer's consent is prohibited, and that the tickets are issued to the fan's own account and name;
- that the purchase cannot be cancelled or refunded except when the event is 中止 (cancelled), that no cooling-off applies, and that official resale opens only if the event sells out;
- the Organizer's business details, carried by the Series of the event's Concert: legal name, representative name, business address, business phone number and contact email.

For a resale Checkout, the screen SHALL also say that the tickets are 公式リセール (official resale) tickets sold at face value, listed by fans who cannot attend, and newly issued to the fan's own account and name, and SHALL show as the sale period that resale closes when admission opens, with that date and time.

It SHALL offer to go back and change the number of tickets or the personal details from this screen. The place-order action SHALL state that it pays, with the amount, and SHALL be disabled while the order is being placed.

#### Scenario: Final confirmation shown

- **WHEN** a fan reaches the last step for 2 tickets of 3000 yen
- **THEN** every listed item is shown and the action reads 6,000円を支払って購入する

#### Scenario: Resale final confirmation

- **WHEN** a fan reaches the last step of a resale Checkout for 1 ticket of 5000 yen whose resale closes at 15:00 on the event day
- **THEN** every listed item is shown, the screen says the ticket is an official resale ticket at face value issued in the fan's name, the sale period ends at 15:00 on the event day, and the action reads 5,000円を支払って購入する

#### Scenario: Fan corrects the name

- **WHEN** the fan goes back from the final confirmation to change their name and returns
- **THEN** the final confirmation shows the corrected name and the same hold

#### Scenario: Double tap on the action

- **WHEN** the fan taps the action twice
- **THEN** the order is placed once

### Requirement: Outcome of placing the order

Placing the order SHALL call OrderUseCase.IssueFromCheckout. On success, the checkout SHALL show the completion screen with the event, the number of tickets, the total paid and a link to the Tickets screen. It SHALL then offer to allow notifications when the fan has not allowed them, and to add the app to the home screen when it is not installed. On failure, it SHALL read the Checkout with CheckoutUseCase.Get and say, by its status:
- Expired: that the 15 minutes passed, that the card was not charged, that the released card authorization may still show on the card statement for a few days, and offer to start again;
- Released with a commit time: that the card could not be charged, and offer to start again;
- Released without a commit time: that it was replaced by a newer checkout, for example in another tab, and offer to go to it;
- Held: that the card authentication is not complete, to finish it and try again;
- Committed or Completed: that the purchase is being completed and the tickets will appear in the Tickets screen shortly.

#### Scenario: Purchase placed

- **WHEN** the purchase succeeds
- **THEN** the completion screen shows 2 tickets and 6,000円 with a link to the Tickets screen

#### Scenario: Hold ended at the last step

- **WHEN** placing the order fails because the hold has ended
- **THEN** the screen says the 15 minutes passed and the card was not charged, and offers to start again

#### Scenario: Charge still completing

- **WHEN** placing the order fails with Unavailable after the commit
- **THEN** the screen says the purchase is being completed and the tickets will appear shortly

### Requirement: A sale that requires verification

When the sale requires verification, the checkout SHALL say so before the fan starts, and when the fan has no Active IdentityVerification it SHALL offer the way to verify instead of starting the checkout. A FailedPrecondition from CheckoutService.Start for a fan without an Active IdentityVerification SHALL be shown as the missing verification, not as a reached limit.

#### Scenario: Unverified fan on a verified sale
- **WHEN** a fan without an IdentityVerification opens the checkout of a sale that requires JPKI-only
- **THEN** the screen says the sale requires マイナンバーカード verification and offers to verify, and no checkout is started

#### Scenario: Verified fan on a verified sale
- **WHEN** a fan with an Active JPKI IdentityVerification opens the same checkout
- **THEN** the checkout starts as usual

### Requirement: Personal details, prefilled

The checkout SHALL ask for the 本人確認 full name and phone number, prefilled with the full name and phone number on the fan's User. The phone number field SHALL accept a Japanese domestic number or an E.164 number, with or without separators, and send it in E.164 form, as the lottery entry screen does. It SHALL state that the name and phone number are saved on the fan's account and shown on the face of their tickets.

#### Scenario: Returning fan

- **WHEN** a fan whose User has a full name and phone number reaches the personal details step
- **THEN** their name and phone number are already filled in and can be edited

### Requirement: The kept referral code goes with the checkout

When continuing holds the tickets with CheckoutService.Start, the checkout SHALL send the referral code kept on the device by the Event page when the code has not expired and was kept for the Series of the checkout's event, and SHALL send no code otherwise. Sending a code SHALL NOT change anything the fan sees. Placing the order, failing or leaving the checkout SHALL leave the kept code on the device.

#### Scenario: Purchase three days after the link
- **WHEN** a fan who opened a link with `ref=member-a` for an event of XX Tour 2026 three days ago continues the checkout of any event of XX Tour 2026
- **THEN** Start is called with the code `member-a`

#### Scenario: Code expired
- **WHEN** the fan opened that link 8 days ago
- **THEN** Start is called without a code

#### Scenario: Another Series
- **WHEN** the kept code was kept for XX Tour 2026 and the fan checks out an event of another Series
- **THEN** Start is called without a code

#### Scenario: Direct visit
- **WHEN** no code is kept on the device
- **THEN** Start is called without a code

### Requirement: Checkout steps and the purchase start are reported

Each time the checkout shows one of its steps (count, personal details, payment, final confirmation, done, outcome, or the verification notice), it SHALL send one usage analytics event naming the step, with the Event and the TicketType. When continuing from the count step holds the tickets, it SHALL send one purchase-initiated event with the Event, the TicketType, the ticket count and the price band of the TicketType.

#### Scenario: Fan reaches the final confirmation
- **WHEN** a fan holds 2 tickets, enters personal details and authorizes the card
- **THEN** one purchase-initiated event and one step event each for personal details, payment and final confirmation are sent

#### Scenario: Verification notice instead of a hold
- **WHEN** the checkout shows the verification notice, on opening or because holding the tickets was refused for the fan's verification
- **THEN** one step event naming the verification notice is sent and no purchase-initiated event is sent
