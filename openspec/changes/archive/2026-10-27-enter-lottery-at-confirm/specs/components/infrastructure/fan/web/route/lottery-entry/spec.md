## MODIFIED Requirements

### Requirement: Saved details are prefilled

When the fan has given a full name and phone number before, the screen SHALL open with them filled in, and SHALL say that the details are saved on the account and shown on the face of the fan's tickets. A change the fan makes on the screen SHALL be saved on the account when the fan authorizes their card (LotteryEntryService.AuthorizeCard). The screen SHALL make the entry with LotteryEntryService.AuthorizeCard, for the chosen ticket count, and Confirm, and SHALL show the entry as made only after Confirm succeeds. When the fan changes the ticket count after authorizing, the screen SHALL authorize the card again for the new count.

#### Scenario: Returning fan
- **WHEN** a fan who entered a lottery before with 山田 花子 and `+819012345678` opens the entry screen for another TicketType
- **THEN** the name and phone number fields show 山田 花子 and 090-1234-5678

#### Scenario: First entry
- **WHEN** a fan who never gave a name or phone number opens the entry screen
- **THEN** both fields are empty

#### Scenario: Count changed after authorizing
- **WHEN** the fan authorizes their card for 2 tickets, goes back and chooses 3 tickets
- **THEN** AuthorizeCard is called again for 3 tickets before the fan confirms

### Requirement: The kept referral code goes with the entry

When the screen authorizes the card with LotteryEntryService.AuthorizeCard, it SHALL send the referral code kept on the device by the Event page when the code has not expired and was kept for the Series of the entry's event, and SHALL send no code otherwise. Sending a code SHALL NOT change anything the fan sees. Confirming, failing or leaving the entry SHALL leave the kept code on the device.

#### Scenario: Entry from a referral link
- **WHEN** a fan who opened a link with `ref=member-a` for an event of XX Tour 2026 yesterday authorizes their card for a TicketType of an event of XX Tour 2026
- **THEN** AuthorizeCard is called with the code `member-a`

#### Scenario: Another Series
- **WHEN** the kept code was kept for another Series
- **THEN** AuthorizeCard is called without a code

#### Scenario: Code expired
- **WHEN** the fan opened the link 8 days ago
- **THEN** AuthorizeCard is called without a code

### Requirement: Starting and submitting an entry are reported

When the screen first authorizes the card with LotteryEntryService.AuthorizeCard, it SHALL send one usage analytics event with the Event, the TicketType and the ticket count. When confirming the entry succeeds, it SHALL send one entry-submitted event with the same values.

#### Scenario: Entry submitted
- **WHEN** a fan authorizes their card for 2 tickets and confirms the entry
- **THEN** one entry-started event and one entry-submitted event are sent, each with the count 2

## ADDED Requirements

### Requirement: A refused entry is explained

When Confirm fails with FailedPrecondition or InvalidArgument, the screen SHALL show that the entry was not made and that nothing will be charged, and SHALL say that the fan already has an entry for the TicketType when they do, or that the window has closed when it has.

#### Scenario: Window closed while confirming
- **WHEN** the fan completes card authentication and Confirm fails with FailedPrecondition because the window closed
- **THEN** the screen shows that the entry was not made, that the window has closed and that nothing will be charged
