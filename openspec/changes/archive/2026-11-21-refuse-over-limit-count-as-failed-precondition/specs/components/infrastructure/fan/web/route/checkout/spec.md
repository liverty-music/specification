## MODIFIED Requirements

### Requirement: Card payment

The checkout SHALL take the card through a card form that also offers Apple Pay or Google Pay where the device supports them. It SHALL authorize the card with CheckoutUseCase.AuthorizeCard, sending the full name and phone number, and complete the card issuer's authentication in the page. It SHALL say that the card is not charged until the order is placed. When authorizing fails with InvalidArgument, the checkout SHALL return to the personal details step and say that the name or phone number could not be used, keeping the hold.

#### Scenario: Card declined

- **WHEN** the card issuer declines the authentication
- **THEN** the screen says the card could not be used and lets the fan try another card without losing the hold

#### Scenario: Hold ended before authorizing

- **WHEN** authorizing fails because the hold has ended
- **THEN** the screen says the 15 minutes have passed and offers to start again

#### Scenario: Name or phone number refused

- **WHEN** authorizing fails with InvalidArgument
- **THEN** the screen returns to the personal details step with the entered name and phone number and says to check them, and the hold continues

## ADDED Requirements

### Requirement: Only a count within the per-account limit is held

Continuing SHALL call CheckoutUseCase.Start only with a count from 1 to the event's per-account limit. For any other count it SHALL say how many tickets one account may hold for the event and hold nothing.

#### Scenario: Count above the limit is not sent

- **WHEN** the count to hold is 5 and the event's per-account limit is 4
- **THEN** the screen says one account may hold 4 tickets for the event and CheckoutUseCase.Start is not called
