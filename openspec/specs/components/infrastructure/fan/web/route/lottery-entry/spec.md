# components/infrastructure/fan/web/route/lottery-entry Specification

## Purpose
The fan's lottery entry screen, where a fan picks a ticket count of one seat type (a TicketStock) in one Lottery sale, enters their 本人確認 (identity check) details and authorizes their card before confirming the LotteryEntry.

## Requirements

### Requirement: Phone number entry

The 本人確認 phone number field SHALL accept either a Japanese domestic number — 10 or 11 digits starting with 0 — or an E.164 number, in both cases with or without spaces, hyphens and parentheses. The screen SHALL send the number in E.164 form: a domestic number becomes `+81` followed by the digits without the leading 0, and an E.164 number is sent without its separators. While the entered number fits neither form, the screen SHALL keep the step's continue action disabled and show that the phone number is invalid.

#### Scenario: Domestic number with hyphens

- **WHEN** the fan enters `090-1234-5678` and confirms the entry
- **THEN** the entry is sent with the phone number `+819012345678`

#### Scenario: Landline number

- **WHEN** the fan enters `03 1234 5678` and confirms the entry
- **THEN** the entry is sent with the phone number `+81312345678`

#### Scenario: E.164 number with spaces

- **WHEN** the fan enters `+81 90 1234 5678` and confirms the entry
- **THEN** the entry is sent with the phone number `+819012345678`

#### Scenario: Number fits neither form

- **WHEN** the fan enters `12345` or `9012345678`
- **THEN** the continue action stays disabled and the field shows that the phone number is invalid

### Requirement: Saved details are prefilled

When the fan has given a full name and phone number before, the screen SHALL open with them filled in, and SHALL say that the details are saved on the account and shown on the face of the fan's tickets. A change the fan makes on the screen SHALL be saved on the account when the fan authorizes their card (LotteryEntryService.AuthorizeCard). The screen SHALL make the entry with LotteryEntryService.AuthorizeCard, for the chosen ticket count, and Confirm, and SHALL show the entry as made only after Confirm succeeds. When the fan changes the ticket count after authorizing, the screen SHALL authorize the card again for the new count.

#### Scenario: Returning fan
- **WHEN** a fan who entered a lottery before with 山田 花子 and `+819012345678` opens the entry screen for another sale
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

When the screen first authorizes the card with LotteryEntryService.AuthorizeCard, it SHALL send one usage analytics event with the Event, the TicketStock and the ticket count. When confirming the entry succeeds, it SHALL send one entry-submitted event with the same values.

#### Scenario: Entry submitted
- **WHEN** a fan authorizes their card for 2 tickets and confirms the entry
- **THEN** one entry-started event and one entry-submitted event are sent, each with the count 2

### Requirement: A refused entry is explained

When Confirm fails with FailedPrecondition or InvalidArgument, the screen SHALL show that the entry was not made and that nothing will be charged, and SHALL say that the fan already has an entry in this sale for this event when they do, that the window has closed when it has, that the fan's tickets for the event are of another seat type when they are, or that the per-account limit would be exceeded when it would.

#### Scenario: Window closed while confirming
- **WHEN** the fan completes card authentication and Confirm fails with FailedPrecondition because the window closed
- **THEN** the screen shows that the entry was not made, that the window has closed and that nothing will be charged

#### Scenario: Already entered the sale
- **WHEN** Confirm fails because the fan already entered the sale for the same event for A席 and now chose S席
- **THEN** the screen shows that the entry was not made, that the fan already has an entry in this sale for this event, and that nothing will be charged

### Requirement: The fan enters one seat type

The screen SHALL enter the Lottery sale and the TicketStock it was opened for and SHALL show the stock's event, the sale's name, the seat type's name, the price per ticket and the event's per-account limit, and SHALL not offer a ticket count above the per-account limit.

#### Scenario: Presale entry
- **WHEN** a fan opens the screen for the ファンクラブ先行 sale and the S席 of the 3 November event, priced 8000 yen with a limit of 4
- **THEN** the screen shows ファンクラブ先行, the 3 November event, S席 and 8000 yen, and offers 1 to 4 tickets
