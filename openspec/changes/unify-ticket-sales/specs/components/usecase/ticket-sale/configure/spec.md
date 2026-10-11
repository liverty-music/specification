# Spec Delta

## REMOVED Requirements

### Requirement: Only the owner of a published, timed event with seller details
**Reason**: A sale is now created for a Series with a TicketType per event and either method, and changed through separate window and ticket type edits, so the one create-or-update method goes.
**Migration**: TicketSaleUseCase.Create (usecase/ticket-sale/create) with the method FirstCome keeps these preconditions: the Series' owner only (PermissionDenied), published events with a start time, complete business details of the Organizer, and the end time no later than every event's start time (now FailedPrecondition instead of InvalidArgument).

### Requirement: Create the sale, or update it
**Reason**: Creating and changing a sale are separate methods.
**Migration**: TicketSaleUseCase.Create creates the sale, ending at the earliest event start time when no end time is given; TicketSaleUseCase.SetWindow changes the window and TicketTypeUseCase.Update the price, quantity and per-account limit under the TicketType's price lock and quantity floor.
