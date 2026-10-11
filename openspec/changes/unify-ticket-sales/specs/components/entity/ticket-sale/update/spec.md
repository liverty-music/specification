# Spec Delta

## REMOVED Requirements

### Requirement: Update keeps sold and held tickets covered
**Reason**: The window is the sale's and the price, quantity and per-account limit are a TicketType's, so the one update splits in two.
**Migration**: TicketSale.SetWindow (entity/ticket-sale/set-window) changes the start and end times; TicketType.Update (entity/ticket-type/update) changes the price, quantity and per-account limit and keeps the price lock and the sold-plus-held floor, checked indivisibly.
