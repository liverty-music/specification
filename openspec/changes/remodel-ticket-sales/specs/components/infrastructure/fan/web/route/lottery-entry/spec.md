# Spec Delta

## ADDED Requirements

### Requirement: The fan enters one seat type

The screen SHALL enter the Lottery sale and the TicketStock it was opened for and SHALL show the stock's event, the sale's name, the seat type's name, the price per ticket and the event's per-account limit, and SHALL not offer a ticket count above the per-account limit.

#### Scenario: Presale entry
- **WHEN** a fan opens the screen for the ファンクラブ先行 sale and the S席 of the 3 November event, priced 8000 yen with a limit of 4
- **THEN** the screen shows ファンクラブ先行, the 3 November event, S席 and 8000 yen, and offers 1 to 4 tickets

## MODIFIED Requirements

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

## REMOVED Requirements

### Requirement: The fan enters one ticket type

**Reason**: TicketType is replaced by the sale and the TicketStock.
**Migration**: See "The fan enters one seat type".
