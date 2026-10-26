## REMOVED Requirements

### Requirement: Draw outcome is recorded together
**Reason**: The outcome of a sale is now recorded one TicketType at a time, before any card is charged, and the sale's draw time is recorded on its own once every TicketType is recorded.
**Migration**: Use LotteryEntry.RecordDrawOutcome for each TicketType and TicketSale.RecordDraw for the sale.
