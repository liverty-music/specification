## REMOVED Requirements

### Requirement: Sold listings left to finish
**Reason**: Its only reader, the 1-minute run of ResaleListingUseCase.RefundSold, is replaced by one RefundSold workflow per listing made Sold, started from Order.Issue's announcement.
**Migration**: None; the operation is removed.
