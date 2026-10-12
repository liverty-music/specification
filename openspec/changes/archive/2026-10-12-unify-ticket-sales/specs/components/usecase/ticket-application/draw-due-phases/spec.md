# Spec Delta

## REMOVED Requirements

### Requirement: Draw within one minute after the window closes
**Reason**: TicketApplication is renamed LotteryEntry and enters a TicketType instead of a LotterySalesPhase; the applicant's name and phone number move to the User.
**Migration**: The behavior continues in `components/usecase/lottery-entry/draw-due-sales`; the data moves in this change's migration.
