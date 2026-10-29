# Spec Delta

## REMOVED Requirements

### Requirement: Only the Series' Organizer changes a ticket type

**Reason**: TicketType is replaced by SeatType and TicketStock, whose price and quantity never change.
**Migration**: A mistaken SeatType or TicketStock is deleted and created again before any Order names it (components/usecase/seat-type/delete, components/usecase/ticket-stock/delete).

### Requirement: A lottery ticket type changes only before its sale opens

**Reason**: Price and quantity never change, so there is nothing to change before a sale opens.
**Migration**: None.

### Requirement: Store the change

**Reason**: Price and quantity never change; more tickets are a new SeatType and TicketStock.
**Migration**: None.
