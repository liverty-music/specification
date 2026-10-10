# Spec Delta

## REMOVED Requirements

### Requirement: Holding an amount
**Reason**: TicketApplication is renamed LotteryEntry and enters a TicketType instead of a LotterySalesPhase; the applicant's name and phone number move to the User.
**Migration**: The behavior continues in `components/entity/lottery-entry/create-authorization`; the data moves in this change's migration.
