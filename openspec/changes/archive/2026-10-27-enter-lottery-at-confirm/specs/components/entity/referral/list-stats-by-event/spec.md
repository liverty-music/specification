## REMOVED Requirements

### Requirement: Paid Orders of an event per referral code
**Reason**: The Referral entity is folded into the purchases; the grouping reads the purchases' referral codes.
**Migration**: Order.ListReferralStatsByEvent returns the same groups.
