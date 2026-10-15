## ADDED Requirements

### Requirement: The kept referral code goes with the entry

When the screen starts the entry with LotteryEntryService.Start, it SHALL send the referral code kept on the device by the Event page when the code has not expired and was kept for the Series of the entry's event, and SHALL send no code otherwise. Sending a code SHALL NOT change anything the fan sees. Confirming, failing or leaving the entry SHALL leave the kept code on the device.

#### Scenario: Entry from a referral link
- **WHEN** a fan who opened a link with `ref=member-a` for an event of XX Tour 2026 yesterday starts an entry for a TicketType of an event of XX Tour 2026
- **THEN** Start is called with the code `member-a`

#### Scenario: Another Series
- **WHEN** the kept code was kept for another Series
- **THEN** Start is called without a code

#### Scenario: Code expired
- **WHEN** the fan opened the link 8 days ago
- **THEN** Start is called without a code
