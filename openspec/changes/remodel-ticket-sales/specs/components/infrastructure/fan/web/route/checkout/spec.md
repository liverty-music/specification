# Spec Delta

## ADDED Requirements

### Requirement: 特商法 final confirmation of a first-come purchase

Before placing the order, the checkout SHALL show on one screen:
- the event, its date, venue, and open and start times;
- the seat type's name, the number of tickets, with the price per ticket and the total to pay, 税込;
- the payment method, credit card, with the card brand and last four digits, and that the card is charged when the order is placed;
- that the tickets are available in the app's Tickets screen immediately after purchase;
- the sale period;
- that resale of the tickets without the Organizer's consent is prohibited, and that the tickets are issued to the fan's own account and name;
- that the purchase cannot be cancelled or refunded except when the event is 中止 (cancelled), that no cooling-off applies, and that official resale opens only if the seat type sells out for the event;
- the Organizer's business details, carried by the Series of the event's Concert: legal name, representative name, business address, business phone number and contact email.

It SHALL offer to go back and change the number of tickets or the personal details from this screen. The place-order action SHALL state that it pays, with the amount, and SHALL be disabled while the order is being placed.

#### Scenario: Final confirmation shown

- **WHEN** a fan reaches the last step for 2 S席 tickets of 3000 yen
- **THEN** every listed item is shown, including S席, and the action reads 6,000円を支払って購入する

#### Scenario: Fan corrects the name

- **WHEN** the fan goes back from the final confirmation to change their name and returns
- **THEN** the final confirmation shows the corrected name and the same hold

#### Scenario: Double tap on the action

- **WHEN** the fan taps the action twice
- **THEN** the order is placed once


## MODIFIED Requirements

### Requirement: Choose the count and hold the tickets

The checkout SHALL open from an event's ticket section for a signed-in fan, on one TicketStock of the event, with the event's open FirstCome sale. It SHALL show the seat type's name and offer a count from 1 to the event's per-account limit, showing the price per ticket and the total, both 税込 (tax-inclusive). Continuing SHALL hold the tickets with CheckoutUseCase.Start and show how long the hold lasts, counting down from its expiry. When continuing fails with FailedPrecondition, the checkout SHALL re-read the event's sales with TicketSaleUseCase.ListByEvent and say the sale has ended, sold out or was cancelled when the sale's window is closed or the TicketStock is SoldOut, that the fan's tickets for the event are of another seat type when they are, and that the per-account limit was reached otherwise. While a request is in flight, the continue action SHALL be disabled. Reopening the checkout during the hold SHALL resume it with the same countdown.

#### Scenario: Fan picks two tickets

- **WHEN** a fan picks 2 S席 tickets of 3000 yen
- **THEN** the screen shows S席, the total shows 6,000円（税込） and continuing holds them with a 15-minute countdown

#### Scenario: Fan reloads mid-checkout

- **WHEN** the fan reloads the page 5 minutes into the hold
- **THEN** the checkout resumes with 10 minutes left

#### Scenario: Last tickets in other checkouts

- **WHEN** continuing fails because the remaining tickets are held by others
- **THEN** the screen says the tickets are sold out for now, that other fans are checking out, and that they may be available again in a few minutes

#### Scenario: Over the limit

- **WHEN** continuing fails because the fan would exceed the per-account limit
- **THEN** the screen says how many tickets one account may hold for the event, counting the tickets it already holds and has applied for

#### Scenario: Another seat type held

- **WHEN** continuing fails because the fan holds A席 tickets for the event and chose S席
- **THEN** the screen says the fan's tickets for this date are A席 and one account holds one seat type per date

#### Scenario: Sale ended before continuing

- **WHEN** continuing fails because the sale ended or sold out after the fan opened the checkout
- **THEN** the screen re-reads the sale and says it has ended or sold out, not that the limit was reached

### Requirement: Checkout steps and the purchase start are reported

Each time the checkout shows one of its steps (count, personal details, payment, final confirmation, done, outcome, or the verification notice), it SHALL send one usage analytics event naming the step, with the Event and the TicketStock. When continuing from the count step holds the tickets, it SHALL send one purchase-initiated event with the Event, the TicketStock, the ticket count and the price band of its seat type.

#### Scenario: Fan reaches the final confirmation
- **WHEN** a fan holds 2 tickets, enters personal details and authorizes the card
- **THEN** one purchase-initiated event and one step event each for personal details, payment and final confirmation are sent

#### Scenario: Verification notice instead of a hold
- **WHEN** the checkout shows the verification notice, on opening or because holding the tickets was refused for the fan's verification
- **THEN** one step event naming the verification notice is sent and no purchase-initiated event is sent


## REMOVED Requirements

### Requirement: 特商法 final confirmation

**Reason**: The checkout no longer buys resale tickets; the resale purchase and its 特商法 (Specified Commercial Transactions Act) confirmation move to the change resell-tickets-by-lottery.
**Migration**: See "特商法 final confirmation of a first-come purchase".
