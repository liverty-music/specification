# Spec Delta

## REMOVED Requirements

### Requirement: Apply with an authenticated hold
**Reason**: TicketApplication is renamed LotteryEntry and enters a TicketType instead of a LotterySalesPhase; the applicant's name and phone number move to the User.
**Migration**: The behavior continues in `components/usecase/lottery-entry/enter`; the data moves in this change's migration.

### Requirement: Verification gate
**Reason**: TicketApplication is renamed LotteryEntry and enters a TicketType instead of a LotterySalesPhase; the applicant's name and phone number move to the User.
**Migration**: The behavior continues in `components/usecase/lottery-entry/enter`; the data moves in this change's migration.
