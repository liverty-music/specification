# Spec Delta

## REMOVED Requirements

### Requirement: Update acts for the caller's own active Organizer

**Reason**: The ticket type service is removed with TicketType.
**Migration**: The organizer seat type and ticket stock services create and delete seat types and stocks (components/adapter/organizer/api/rpc/seat-type, components/adapter/organizer/api/rpc/ticket-stock).

### Requirement: Update names the ticket type and its values

**Reason**: The ticket type service is removed with TicketType.
**Migration**: None.
