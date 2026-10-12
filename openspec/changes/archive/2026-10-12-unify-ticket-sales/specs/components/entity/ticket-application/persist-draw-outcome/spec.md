# Spec Delta

## REMOVED Requirements

### Requirement: Draw outcome is recorded together
**Reason**: TicketApplication is renamed LotteryEntry and enters a TicketType instead of a LotterySalesPhase; the applicant's name and phone number move to the User.
**Migration**: The behavior continues in `components/entity/lottery-entry/persist-draw-outcome`; the data moves in this change's migration.
