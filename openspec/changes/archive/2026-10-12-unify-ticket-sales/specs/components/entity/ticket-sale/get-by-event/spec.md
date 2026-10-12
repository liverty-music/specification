# Spec Delta

## REMOVED Requirements

### Requirement: The event's sale
**Reason**: An event can be offered by several sales, so there is no single sale to get by event.
**Migration**: TicketSale.ListByEvent (entity/ticket-sale/list-by-event) returns every sale of the event with its TicketTypes and held counts, ordered by start time; an event without a sale gives an empty list instead of NotFound.
