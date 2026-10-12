# Spec Delta

## REMOVED Requirements

### Requirement: Sale and its state for an event
**Reason**: An event can be offered by several sales, so the fan read returns them all.
**Migration**: TicketSaleUseCase.ListByEvent (usecase/ticket-sale/list-by-event) returns the event's sales with their TicketType for the event and, for a first-come TicketType, its state and LowStock; an unpublished event or an event without a sale gives an empty list instead of NotFound.
