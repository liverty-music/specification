## ADDED Requirements

### Requirement: The loss email is sent as given
SendLossEmail SHALL take a LotteryEntry's id, the email address of its Order's user and the finished message, and send the message as an email to that address, tagged with the entry's id. Whether the email is due, and recording that it was sent, are the caller's (LotteryEntry.LossEmailDue, LotteryEntry.MarkLossEmailSent). It SHALL fail with InvalidArgument when the address or the message is empty and with Unavailable when email cannot be sent.

#### Scenario: Email sent
- **WHEN** SendLossEmail is called with an address and a message
- **THEN** one email with the message is sent to the address

#### Scenario: Mail unavailable
- **WHEN** email cannot be sent
- **THEN** SendLossEmail fails with Unavailable

## REMOVED Requirements

### Requirement: One loss email per entry

**Reason**: The mail adapter decided whether the email was due and recorded the send. The adapter now only sends; the decision is the entity's and the record the usecase's.
**Migration**: LotteryEntry.LossEmailDue decides whether the email is due and the notification usecase records the send (LotteryEntry.MarkLossEmailSent); its scenarios "Redelivered event" and "Mail unavailable" are covered by usecase/notification/send-lottery-loss ("Loss announced twice", "Mail unavailable").
