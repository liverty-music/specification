# components/entity/lottery-entry/send-loss-email Specification

## Purpose
Sends the email telling the fan of a Lost LotteryEntry that the entry lost, as the caller composed it. Whether the email is due and recording that it was sent are the caller's, so it is sent once per entry.

## Requirements

### Requirement: The loss email is sent as given
SendLossEmail SHALL take a LotteryEntry's id, the email address of its Order's user and the finished message, and send the message as an email to that address, tagged with the entry's id. Whether the email is due, and recording that it was sent, are the caller's (LotteryEntry.LossEmailDue, LotteryEntry.MarkLossEmailSent). It SHALL fail with InvalidArgument when the address or the message is empty and with Unavailable when email cannot be sent.

#### Scenario: Email sent
- **WHEN** SendLossEmail is called with an address and a message
- **THEN** one email with the message is sent to the address

#### Scenario: Mail unavailable
- **WHEN** email cannot be sent
- **THEN** SendLossEmail fails with Unavailable
