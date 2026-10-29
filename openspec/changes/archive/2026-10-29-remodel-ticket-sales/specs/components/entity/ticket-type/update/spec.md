# Spec Delta

## REMOVED Requirements

### Requirement: Update keeps sold and held tickets covered

**Reason**: A SeatType's price and a TicketStock's quantity never change; more tickets are a new SeatType and TicketStock.
**Migration**: A mistake is fixed with SeatType.Delete or TicketStock.Delete and a new create before any Order names the stock.
