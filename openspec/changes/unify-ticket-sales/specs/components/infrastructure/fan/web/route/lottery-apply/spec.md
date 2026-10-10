# Spec Delta

## ADDED Requirements

### Requirement: Saved details are prefilled

When the fan has given a full name and phone number before, the screen SHALL open with them filled in, and SHALL say that the details are saved on the account and shown on the face of the fan's tickets. A change the fan makes on the screen SHALL be saved on the account when the entry is made.

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
