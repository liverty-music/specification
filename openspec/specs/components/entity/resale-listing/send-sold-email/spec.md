# components/entity/resale-listing/send-sold-email Specification

## Purpose
Sends the user of a Sold ResaleListing the email saying their Ticket was resold and how much is refunded, at most once per listing.

## Requirements

### Requirement: One sold email per listing

SendSoldEmail SHALL take a ResaleListing, an email address, a language and the message content, send the email and record its send time on the listing. When the listing already has a sold email send time, it SHALL send nothing. It SHALL fail with Unavailable when mail cannot be sent, recording nothing, so it can be tried again.

#### Scenario: First send
- **WHEN** SendSoldEmail is called for a Sold listing without a send time
- **THEN** one email is sent and the send time is recorded

#### Scenario: Sent before
- **WHEN** SendSoldEmail is called for a listing with a send time
- **THEN** no email is sent

#### Scenario: Mail unavailable
- **WHEN** sending fails
- **THEN** SendSoldEmail fails with Unavailable and no send time is recorded
