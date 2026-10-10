# Spec Delta

## REMOVED Requirements

### Requirement: Every lottery call acts for the caller's own active Organizer
**Reason**: The organizer lottery service is replaced by the organizer ticket sale service, which creates, lists and changes TicketSales.
**Migration**: The behavior continues in `components/adapter/organizer/api/rpc/ticket-sale`; the data moves in this change's migration.
