# components/infrastructure/fan/web/route/lottery-entry Specification

## Purpose
The fan's lottery entry screen, where a fan picks a ticket count for one TicketType, enters their 本人確認 (identity check) details and authorizes their card before confirming the LotteryEntry.

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

When the fan has given a full name and phone number before, the screen SHALL open with them filled in, and SHALL say that the details are saved on the account and shown on the face of the fan's tickets. A change the fan makes on the screen SHALL be saved on the account when the fan authorizes their card (LotteryEntryService.AuthorizeCard). The screen SHALL make the entry with LotteryEntryService.Start, AuthorizeCard and Confirm, and SHALL show the entry as made only after Confirm succeeds.

#### Scenario: Returning fan
- **WHEN** a fan who entered a lottery before with 山田 花子 and `+819012345678` opens the entry screen for another TicketType
- **THEN** the name and phone number fields show 山田 花子 and 090-1234-5678

#### Scenario: First entry
- **WHEN** a fan who never gave a name or phone number opens the entry screen
- **THEN** both fields are empty

### Requirement: The fan enters one ticket type

The screen SHALL enter the TicketType it was opened for and SHALL show that TicketType's event, the sale's name, the price per ticket and the per-account limit, and SHALL not offer a ticket count above the per-account limit.

#### Scenario: Presale entry
- **WHEN** a fan opens the screen for the ファンクラブ先行 TicketType of the 3 November event, priced 8000 yen with a limit of 4
- **THEN** the screen shows ファンクラブ先行, the 3 November event and 8000 yen, and offers 1 to 4 tickets
