# Spec Delta

## REMOVED Requirements

### Requirement: The owner sees its sale with the counts
**Reason**: An event can be offered by several sales, so the Organizer's read lists them all.
**Migration**: TicketSaleUseCase.ListOwnByEvent (usecase/ticket-sale/list-own-by-event) returns each sale of the event with, for a first-come TicketType, its quantity, sold count, held count and state; an event without a sale gives an empty list instead of NotFound.
