## REMOVED Requirements

### Requirement: Withdraw before the draw
**Reason**: A fan can no longer give up a lottery entry, before or after the window closes; a confirmed entry always takes part in the draw.
**Migration**: None for callers: LotteryEntryService.Withdraw is removed in the same change and the lottery entry status screen no longer offers the action. Existing Withdrawn entries are deleted by the schema migration.
