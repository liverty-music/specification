# Spec Delta

## REMOVED Requirements

### Requirement: Result after the draw
**Reason**: TicketApplication is renamed LotteryEntry and enters a TicketType instead of a LotterySalesPhase; the applicant's name and phone number move to the User.
**Migration**: The behavior continues in `components/usecase/lottery-entry/list-by-ticket-type`, whose entries carry Won or Lost after the draw; the data moves in this change's migration.
