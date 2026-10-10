# Spec Delta

## REMOVED Requirements

### Requirement: Active application of an applicant
**Reason**: TicketApplication is renamed LotteryEntry and enters a TicketType instead of a LotterySalesPhase; the applicant's name and phone number move to the User.
**Migration**: The behavior continues in `components/entity/lottery-entry/get-by-ticket-type-and-user`; the data moves in this change's migration.
