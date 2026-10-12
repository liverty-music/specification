# Spec Delta

## REMOVED Requirements

### Requirement: Random order with greedy whole-application fit
**Reason**: TicketApplication is renamed LotteryEntry and enters a TicketType instead of a LotterySalesPhase; the applicant's name and phone number move to the User.
**Migration**: The behavior continues in `components/entity/lottery-entry/run-lottery-draw`; the data moves in this change's migration.

### Requirement: Waitlist in draw order
**Reason**: TicketApplication is renamed LotteryEntry and enters a TicketType instead of a LotterySalesPhase; the applicant's name and phone number move to the User.
**Migration**: The behavior continues in `components/entity/lottery-entry/run-lottery-draw`; the data moves in this change's migration.
