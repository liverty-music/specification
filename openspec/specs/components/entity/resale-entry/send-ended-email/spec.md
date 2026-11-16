# components/entity/resale-entry/send-ended-email Specification

## Purpose
Sends the email telling a fan that their ResaleEntry lapsed or lost, as the caller composed it. Whether the email is due and recording that it was sent are the caller's, so it is sent at most once per entry.

## Requirements

### Requirement: The ended email is sent as given

SendEndedEmail SHALL take a ResaleEntry's id, the fan's email address and a message, and send the message to that address, tagged with the entry's id. Whether the email is due (a Lapsed or Lost entry whose ended email was not sent, ResaleEntry.EndedEmailDue), and recording that it was sent (ResaleEntry.MarkEndedEmailSent), are the caller's. It SHALL fail with InvalidArgument when the address or the message is empty and with Unavailable when email cannot be sent.

#### Scenario: First send
- **WHEN** SendEndedEmail is called with an address and a message
- **THEN** the email is sent

#### Scenario: Mail unavailable
- **WHEN** email cannot be sent
- **THEN** SendEndedEmail fails with Unavailable
