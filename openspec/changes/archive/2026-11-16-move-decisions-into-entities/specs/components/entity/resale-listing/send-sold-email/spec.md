## ADDED Requirements

### Requirement: The sold email is sent as given
SendSoldEmail SHALL take a ResaleListing's id, an email address and the finished message, and send the message as an email to that address, tagged with the listing's id. Whether the email is due, and recording that it was sent, are the caller's (ResaleListing.SoldEmailDue, ResaleListing.MarkSoldEmailSent). It SHALL fail with InvalidArgument when the address or the message is empty and with Unavailable when mail cannot be sent, so it can be tried again.

#### Scenario: First send
- **WHEN** SendSoldEmail is called with an address and a message
- **THEN** one email is sent

#### Scenario: Mail unavailable
- **WHEN** sending fails
- **THEN** SendSoldEmail fails with Unavailable

## REMOVED Requirements

### Requirement: One sold email per listing

**Reason**: The mail adapter decided whether the email was due and recorded the send. The adapter now only sends; the decision is the entity's and the record the usecase's.
**Migration**: ResaleListing.SoldEmailDue decides whether the email is due and the notification usecase records the send (ResaleListing.MarkSoldEmailSent); "Sent before" is covered by usecase/notification/send-resale-sold ("Listing announced twice").
