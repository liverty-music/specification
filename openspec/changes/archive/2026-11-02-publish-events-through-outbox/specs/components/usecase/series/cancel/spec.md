## REMOVED Requirements

### Requirement: Cancellation is announced
**Reason**: The cancellation announcement has no receiver.
**Migration**: None. Series.CancelEvents still makes the Events CANCELLED; nothing listens for the cancellation.
