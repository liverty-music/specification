## MODIFIED Requirements

### Requirement: Outcome of placing the order

Placing the order SHALL call OrderUseCase.Issue for the Checkout. On success, the checkout SHALL show the completion screen with the event, the number of tickets, the total paid and a link to the Tickets screen. It SHALL then offer to allow notifications when the fan has not allowed them, and to add the app to the home screen when it is not installed. On failure, it SHALL read the Checkout with CheckoutUseCase.Get and say, by its status:
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
