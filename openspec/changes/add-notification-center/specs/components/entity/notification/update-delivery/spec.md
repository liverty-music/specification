## REMOVED Requirements

### Requirement: UpdateDelivery stores the outcome and keeps the record
**Reason**: A Notification no longer records its delivery outcome.
**Migration**: NotificationUseCase.Deliver returns the outcome to its caller and logs it for analytics.

### Requirement: A delivered Notification is announced with the change
**Reason**: Nothing reads the delivered announcement except the analytics event notification.delivered, which no analysis uses; delivery rates are read from the analytics log.
**Migration**: None.
