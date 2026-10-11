# Spec Delta

## REMOVED Requirements

### Requirement: Open a hold for an intended application
**Reason**: TicketApplication is renamed LotteryEntry and enters a TicketType instead of a LotterySalesPhase; the applicant's name and phone number move to the User.
**Migration**: The behavior continues in `components/usecase/lottery-entry/authorize`, which opens the hold on the fan's Draft LotteryEntry; the data moves in this change's migration.
