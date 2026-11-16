## MODIFIED Requirements

### Requirement: Loss email after every Lost result

SendLotteryLoss SHALL run for each LotteryEntry announced Lost, by LotteryEntry.PersistDrawOutcome, LotteryEntry.RevertWin or LotteryEntry.EndEnteredByEvent, with its entry. It SHALL read:
- the entry with LotteryEntry.Get and its Order with Order.Get;
- the Order's user with User.Get;
- the Order's TicketStock, its SeatType and its event with TicketStock.Get;
- the event's concert with Concert.ListByIDs.

It SHALL send, with LotteryEntry.SendLossEmail to the user's email address and in the user's preferred language (Japanese when none), a message stating:
- the concert's title, date and venue, and the SeatType and ticket count entered;
- by the entry's lost reason: that the entry was not drawn, that the entry won but its card could not be charged, so the win was cancelled, or that the concert is 中止 (cancelled), so the entry ended;
- that the card was not charged, and that the amount held on the card is given back, which may still show on the card statement for a few days.

When reading or sending fails, SendLotteryLoss SHALL fail with that error and is run again; it SHALL send the email only while none has been sent for the entry (LotteryEntry.LossEmailDue) and then record the send (LotteryEntry.MarkLossEmailSent), so a run again after the email was sent sends no second email.

#### Scenario: Entry not drawn
- **WHEN** a fan's entry for 2 tickets is announced Lost with the lost reason "not drawn"
- **THEN** the fan receives one email with the concert, the SeatType, 2 tickets, that the entry was not drawn and that nothing is charged

#### Scenario: Card could not be charged
- **WHEN** a fan's entry is announced Lost with the lost reason "card could not be charged"
- **THEN** the fan receives one email saying the entry won but the card could not be charged, so the win was cancelled

#### Scenario: Concert cancelled email
- **WHEN** a fan's entry is announced Lost with the lost reason "concert cancelled", whether it was Entered or Won
- **THEN** the fan receives one email saying the concert is cancelled, so the entry ended, and that nothing is charged; it does not say the entry was not drawn

#### Scenario: Loss announced twice
- **WHEN** the same announcement is delivered twice
- **THEN** the fan receives one email

#### Scenario: Mail unavailable
- **WHEN** LotteryEntry.SendLossEmail fails with Unavailable
- **THEN** SendLotteryLoss fails and the email is sent when it runs again
