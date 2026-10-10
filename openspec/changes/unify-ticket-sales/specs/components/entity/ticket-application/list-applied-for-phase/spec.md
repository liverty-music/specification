# Spec Delta

## REMOVED Requirements

### Requirement: Draw candidates
**Reason**: TicketApplication is renamed LotteryEntry and enters a TicketType instead of a LotterySalesPhase; the applicant's name and phone number move to the User.
**Migration**: The behavior continues in `components/entity/lottery-entry/list-entered-for-ticket-type`; the data moves in this change's migration.
