## ADDED Requirements

### Requirement: A new entry is Entered

A LotteryEntry SHALL be created in state Entered, with its card authorization and without a draw position.

#### Scenario: New entry
- **WHEN** a LotteryEntry is created
- **THEN** its state is Entered, it has its card authorization and it has no draw position

## REMOVED Requirements

### Requirement: A new entry starts as a Draft
**Reason**: An entry is made only when the fan confirms; there is no Draft.
**Migration**: Replaced by "A new entry is Entered". The schema migration deletes the Draft entries.

### Requirement: Confirmable only as a Draft with a card authorization
**Reason**: There is no Draft to confirm. LotteryEntryUseCase.Confirm makes the entry from an Authorized card authorization.
**Migration**: The CardAuthorization rule "A card authorization confirms a purchase only when authorized for its amount" decides.

### Requirement: Active entries
**Reason**: Withdrawn is removed, so every entry counts.
**Migration**: None.

### Requirement: Withdrawable only before the draw
**Reason**: A fan cannot withdraw an entry.
**Migration**: None; LotteryEntryService.Withdraw was removed in proto v0.98.0.
