# Spec Delta

## REMOVED Requirements

### Requirement: The applicant is the signed-in caller
**Reason**: The applicant is now the LotteryEntry's user, and the calls take a TicketType or a LotteryEntry instead of a LotterySalesPhase.
**Migration**: Replaced by "The fan entering is the signed-in caller" in `components/adapter/fan/api/rpc/lottery-entry`. CreateAuthorization and Apply become Start, AuthorizeCard and Confirm; GetApplication and GetResult become ListByTicketType, whose entries carry Won or Lost after the draw.

### Requirement: Withdrawal names the phase, not the application
**Reason**: LotterySalesPhase is removed, and Withdraw is a custom method on the LotteryEntry itself.
**Migration**: Withdraw takes the LotteryEntry id (`components/adapter/fan/api/rpc/lottery-entry`, "The fan entering is the signed-in caller").

### Requirement: Lottery requests are validated at the boundary
**Reason**: Requests name a TicketType or a LotteryEntry, and the identity rule is the User's personal details rule.
**Migration**: Replaced by "Lottery entry requests are validated at the boundary" in `components/adapter/fan/api/rpc/lottery-entry`.
