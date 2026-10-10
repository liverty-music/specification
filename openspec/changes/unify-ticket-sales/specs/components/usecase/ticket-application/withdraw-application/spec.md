# Spec Delta

## REMOVED Requirements

### Requirement: Withdraw before the draw
**Reason**: TicketApplication is renamed LotteryEntry and enters a TicketType instead of a LotterySalesPhase; the applicant's name and phone number move to the User.
**Migration**: The behavior continues in `components/usecase/lottery-entry/withdraw-entry`; the data moves in this change's migration.
