## ADDED Requirements

### Requirement: The ended email is sent as given

SendEndedEmail SHALL take a ResaleEntry's id, the fan's email address and a message, and send the message to that address, tagged with the entry's id. Whether the email is due (a Lapsed or Lost entry whose ended email was not sent, ResaleEntry.EndedEmailDue), and recording that it was sent (ResaleEntry.MarkEndedEmailSent), are the caller's. It SHALL fail with InvalidArgument when the address or the message is empty and with Unavailable when email cannot be sent.

#### Scenario: First send
- **WHEN** SendEndedEmail is called with an address and a message
- **THEN** the email is sent

#### Scenario: Mail unavailable
- **WHEN** email cannot be sent
- **THEN** SendEndedEmail fails with Unavailable

## REMOVED Requirements

### Requirement: One email per ended entry

**Reason**: The mail adapter decided whether the email was due and recorded the send. The adapter now only sends; the decision is the entity's and the record the usecase's.
**Migration**: ResaleEntry.EndedEmailDue decides whether the email is due (Lapsed or Lost, not yet sent) and the notification usecase records the send (ResaleEntry.MarkEndedEmailSent); "Sent already" is covered by usecase/notification/send-resale-entry-ended ("Run again after the email was sent"), and an Entered or Won entry gets no ended email because the usecase sends it only for a Lapsed or Lost entry.
