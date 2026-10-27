## REMOVED Requirements

### Requirement: At most one active entry per account per ticket type
**Reason**: There is no Draft; an entry is made once, when the fan confirms.
**Migration**: LotteryEntry.Create stores the entry and keeps one per account and TicketType.
