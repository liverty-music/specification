## MODIFIED Requirements

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
