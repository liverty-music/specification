# components/entity/resale-listing/send-sold-email Specification

## Purpose
Sends the user of a Sold ResaleListing the email saying their Ticket was resold and how much is refunded, as the caller composed it. Whether the email is due and recording that it was sent are the caller's, so it is sent at most once per listing.

## Requirements

### Requirement: The sold email is sent as given
SendSoldEmail SHALL take a ResaleListing's id, an email address and the finished message, and send the message as an email to that address, tagged with the listing's id. Whether the email is due, and recording that it was sent, are the caller's (ResaleListing.SoldEmailDue, ResaleListing.MarkSoldEmailSent). It SHALL fail with InvalidArgument when the address or the message is empty and with Unavailable when mail cannot be sent, so it can be tried again.

#### Scenario: First send
- **WHEN** SendSoldEmail is called with an address and a message
- **THEN** one email is sent

#### Scenario: Mail unavailable
- **WHEN** sending fails
- **THEN** SendSoldEmail fails with Unavailable
