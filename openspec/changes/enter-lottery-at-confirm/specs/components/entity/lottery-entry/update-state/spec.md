## REMOVED Requirements

### Requirement: Update the state
**Reason**: Its only caller, Confirm, now creates the entry Entered; the draw records its outcome with LotteryEntry.PersistDrawOutcome.
**Migration**: None.
