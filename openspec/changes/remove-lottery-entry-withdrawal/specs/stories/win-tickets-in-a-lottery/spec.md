## ADDED Requirements

### Requirement: Only a confirmed entry takes part in the draw

Once a fan confirms their entry with LotteryEntryUseCase.Confirm, the entry SHALL take part in the draw and SHALL NOT be given up. Before confirming, a fan SHALL be able to change the ticket count with LotteryEntryUseCase.Start, which releases any card authorization already opened for the entry. A Draft the fan never confirmed SHALL take no part in the draw, and its card authorization SHALL be released at the draw.

#### Scenario: Count changed before confirming
- **WHEN** a fan authorizes their card for an entry of 2 tickets, changes it to 3 tickets before confirming, authorizes their card again and confirms
- **THEN** the first card authorization is released and only the 3-ticket entry takes part in the draw

#### Scenario: Entry left unconfirmed
- **WHEN** a fan authorizes their card but leaves before confirming, and the window closes
- **THEN** the card authorization is released at the draw, the fan is never charged, and the entry takes no part in the draw

## REMOVED Requirements

### Requirement: A fan can withdraw before the draw
**Reason**: A fan can no longer withdraw a lottery entry. The rule for an unconfirmed Draft moves to "Only a confirmed entry takes part in the draw".
**Migration**: The E2E test of "Withdraw and enter again" is removed; the test of "Entry left unconfirmed" moves to the new requirement.
