## Purpose

NotificationUseCase.SendLotteryLoss tells a fan that their lottery entry lost and that nothing is charged: an email, and a push notification that opens the event.

## ADDED Requirements

### Requirement: Loss email after every Lost result

SendLotteryLoss SHALL run for each lottery result announced Lost, with its entry. It SHALL read:
- the entry with LotteryEntry.Get;
- the entry's user with User.Get;
- the entry's TicketType and its event with TicketType.Get;
- the event's concert with Concert.ListByIDs.

It SHALL send, with LotteryEntry.SendLossEmail to the user's email address and in the user's preferred language (Japanese when none), a message stating:
- the concert's title, date and venue, and the TicketType and ticket count entered;
- that the entry was not drawn, or, for a result from a failed capture, that the entry won but its card could not be charged, so the win was cancelled;
- that the card was not charged, and that the amount held on the card is given back, which may still show on the card statement for a few days.

When reading or sending fails, SendLotteryLoss SHALL fail with that error and is run again; LotteryEntry.SendLossEmail keeps it to one email per entry.

#### Scenario: Entry not drawn
- **WHEN** a fan's entry for 2 tickets is announced Lost by the draw
- **THEN** the fan receives one email with the concert, the TicketType, 2 tickets, that the entry was not drawn and that nothing is charged

#### Scenario: Card could not be charged
- **WHEN** a fan's entry is announced Lost from a failed capture
- **THEN** the fan receives one email saying the entry won but the card could not be charged, so the win was cancelled

#### Scenario: Result announced twice
- **WHEN** the same announcement is delivered twice
- **THEN** the fan receives one email

#### Scenario: Mail unavailable
- **WHEN** LotteryEntry.SendLossEmail fails with Unavailable
- **THEN** SendLotteryLoss fails and the email is sent when it runs again

### Requirement: Push notification after the email

After the email is sent, SendLotteryLoss SHALL request a notification of type lottery_loss for the entry's user with NotificationUseCase.Deliver, saying the entry lost in the user's language and opening the event's page when tapped. A user with no registered browser receives the email only. If SendLotteryLoss stops between requesting the notification and finishing, a run again can push a second notification; the email is still sent once.

#### Scenario: Fan allowed notifications
- **WHEN** the entry's user has a registered browser
- **THEN** a lottery_loss notification is pushed and opens the event's page
