# Spec Delta

## REMOVED Requirements

### Requirement: Price, quantity and per-account limit

**Reason**: TicketType is replaced by SeatType and TicketStock. The price is on SeatType, the quantity on TicketStock and the per-account limit on Event.
**Migration**: See components/entity/seat-type, components/entity/ticket-stock and components/entity/event; the migration in this change's tasks turns every TicketType into a SeatType and TicketStock.

### Requirement: Amount for a requested count

**Reason**: TicketType is replaced by SeatType and TicketStock. The amount is the SeatType's.
**Migration**: See components/entity/seat-type, components/entity/ticket-stock and components/entity/event; the migration in this change's tasks turns every TicketType into a SeatType and TicketStock.

### Requirement: Room under the per-account limit

**Reason**: TicketType is replaced by SeatType and TicketStock. The limit is checked once for the event, across every sale and seat type.
**Migration**: See components/entity/seat-type, components/entity/ticket-stock and components/entity/event; the migration in this change's tasks turns every TicketType into a SeatType and TicketStock.

### Requirement: Remaining tickets

**Reason**: TicketType is replaced by SeatType and TicketStock. The remaining tickets are the TicketStock's, shared by every sale of the event.
**Migration**: See components/entity/seat-type, components/entity/ticket-stock and components/entity/event; the migration in this change's tasks turns every TicketType into a SeatType and TicketStock.

### Requirement: Sale state at a time

**Reason**: TicketType is replaced by SeatType and TicketStock. The stock's state is the TicketStock's; whether a sale is open is the TicketSale's window.
**Migration**: See components/entity/seat-type, components/entity/ticket-stock and components/entity/event; the migration in this change's tasks turns every TicketType into a SeatType and TicketStock.

### Requirement: Price fixed while tickets are held or sold

**Reason**: TicketType is replaced by SeatType and TicketStock. A SeatType's price never changes.
**Migration**: See components/entity/seat-type, components/entity/ticket-stock and components/entity/event; the migration in this change's tasks turns every TicketType into a SeatType and TicketStock.

### Requirement: Resale opens when the ticket type sells out

**Reason**: TicketType is replaced by SeatType and TicketStock. Resale belongs to the TicketStock and is open while it is sold out.
**Migration**: See components/entity/seat-type, components/entity/ticket-stock and components/entity/event; the migration in this change's tasks turns every TicketType into a SeatType and TicketStock.

### Requirement: Resale open at a time

**Reason**: TicketType is replaced by SeatType and TicketStock. Resale belongs to the TicketStock.
**Migration**: See components/entity/seat-type, components/entity/ticket-stock and components/entity/event; the migration in this change's tasks turns every TicketType into a SeatType and TicketStock.

### Requirement: Resale available at a time

**Reason**: TicketType is replaced by SeatType and TicketStock. Resale belongs to the TicketStock.
**Migration**: See components/entity/seat-type, components/entity/ticket-stock and components/entity/event; the migration in this change's tasks turns every TicketType into a SeatType and TicketStock.
