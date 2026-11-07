## ADDED Requirements

### Requirement: A cancelled concert charges no lottery fan

When a member cancels (中止) an Event, the fans of its lottery SHALL NOT be charged for it and SHALL NOT receive Tickets for it. Each Entered entry of the Event SHALL become Lost, its card authorization SHALL be released and its fan SHALL be told by email and push that the concert is cancelled and that nothing is charged, without waiting for the sale's window to close. A Won entry whose charge is still to be attempted SHALL end the same way at that attempt. No new entry for the Event SHALL be accepted. The other dates of the same sale SHALL carry on.

#### Scenario: Cancelled during the window
- **WHEN** a member cancels an Event whose lottery window is open, with two fans Entered
- **THEN** both entries are Lost, both card authorizations are released, each fan receives one email and push saying the concert is cancelled and nothing is charged, and when the window closes nobody is charged and no Ticket is issued

#### Scenario: Cancelled between the draw and the charge
- **WHEN** a draw records a fan's entry Won and the member cancels the Event before the charge
- **THEN** nothing is charged, the entry is Lost, its card authorization is released and the fan is told the concert is cancelled

#### Scenario: Entering after the cancellation
- **WHEN** a fan with the entry screen still open tries to enter after the Event was cancelled
- **THEN** the entry is refused, no entry is made and nothing stays held on the card

#### Scenario: Another date of the sale
- **WHEN** a sale names two Events, and a member cancels one while fans are Entered for both
- **THEN** the entries of the cancelled Event are Lost, and the entries of the other Event stay Entered and are drawn when the window closes
