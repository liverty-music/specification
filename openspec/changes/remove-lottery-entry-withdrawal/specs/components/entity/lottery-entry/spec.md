## MODIFIED Requirements

### Requirement: Confirmable only as a Draft with a card authorization

An entry SHALL be confirmable, that is able to become Entered, only while its state is Draft and it has a card authorization; whether that card authorization confirms it is the CardAuthorization's rule, for the TicketType's price times the ticket count.

#### Scenario: Draft with a card authorization
- **WHEN** the entry is a Draft with a card authorization
- **THEN** it is confirmable

#### Scenario: Draft without a card authorization
- **WHEN** the entry is a Draft with no card authorization
- **THEN** it is not confirmable

#### Scenario: Already entered
- **WHEN** the entry is Entered, Won or Lost
- **THEN** it is not confirmable

## REMOVED Requirements

### Requirement: Active entries
**Reason**: Every entry is now active. Withdrawn, the only state an inactive entry had, is removed.
**Migration**: Code that filtered on activity reads every entry of the account and TicketType; the schema migration deletes the Withdrawn entries.

### Requirement: Withdrawable only before the draw
**Reason**: A fan can no longer withdraw an entry.
**Migration**: None. LotteryEntryUseCase.Withdraw and LotteryEntryService.Withdraw are removed in the same change.
