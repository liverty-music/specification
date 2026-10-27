## Purpose

Emails the fan of a Lost LotteryEntry that the entry lost and records that it was sent, so it is sent once per entry.

## ADDED Requirements

### Requirement: One loss email per entry

SendLossEmail SHALL take a LotteryEntry, the email address of the entry's user and the finished message. When the entry has no loss email send time, it SHALL send the message as an email to that address and then set the entry's loss email send time. When the time is already set, it SHALL send nothing and succeed. A failure between sending and recording can lead to a second email on retry; no other case sends twice. It SHALL fail with InvalidArgument when the address or the message is empty, with Unavailable when email cannot be sent, and with NotFound when no entry has the id.

#### Scenario: Email sent
- **WHEN** SendLossEmail is called for an entry without a loss email send time
- **THEN** one email with the message is sent to the user's address and the loss email send time is set

#### Scenario: Redelivered event
- **WHEN** SendLossEmail is called again for an entry with a loss email send time
- **THEN** it succeeds and no email is sent

#### Scenario: Mail unavailable
- **WHEN** email cannot be sent
- **THEN** SendLossEmail fails with Unavailable and the loss email send time stays unset
