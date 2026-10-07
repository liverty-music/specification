# Spec Delta

## REMOVED Requirements

### Requirement: Reschedule time of the order's event

**Reason**: An Event has no reschedule time. Its only caller was the postponement refund window of RefundOrderUseCase.RefundOrder, which this change removes.
**Migration**: None. Every Event's reschedule time was empty, so no caller ever received a time.
