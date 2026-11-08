## MODIFIED Requirements

### Requirement: Push notification after the email

After the email is sent, SendLotteryLoss SHALL start NotificationUseCase.Deliver for the user of the entry's Order with a notification of type lottery_loss, named after the type and the entry, whose message the Notification entity renders from the entry's lost reason in the user's language, and opening the event's page when tapped. A user with no registered browser receives the email only. A run again for the same entry, after a stop or a repeated announcement, starts no second Deliver, so the fan is pushed once; the email is still sent once.

#### Scenario: Fan allowed notifications
- **WHEN** the user of the entry's Order has a registered browser
- **THEN** a lottery_loss notification is pushed and opens the event's page

#### Scenario: Concert cancelled push
- **WHEN** the user of an entry announced Lost with the lost reason "concert cancelled" has a registered browser
- **THEN** a lottery_loss notification saying the concert is cancelled and that nothing is charged is pushed
