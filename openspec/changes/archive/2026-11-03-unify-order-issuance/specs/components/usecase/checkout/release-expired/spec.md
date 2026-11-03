## REMOVED Requirements

### Requirement: Lapsed holds and leftover card authorizations handled within one minute
**Reason**: The 1-minute sweeper is replaced by workflows: CheckoutUseCase.Expire ends each hold at its expiry, and OrderUseCase.ReleaseCardAuthorization releases the card authorization of each Checkout's Order made Void, started from the Checkout's announcement.
**Migration**: A hold ends at its expiry instead of within the next minute; a card authorization is released by its own workflow, retried for 24 hours and reported to an admin when it cannot finish.

### Requirement: A captured card authorization on an ended checkout is reported
**Reason**: OrderUseCase.ReleaseCardAuthorization ends with FailedPrecondition for a card authorization that was charged, and that run is reported to an admin.
**Migration**: The admin is told through "Workflow Needs Admin" instead of a log line repeated every minute.
