## REMOVED Requirements

### Requirement: Stalled checkouts finished within one minute
**Reason**: OrderUseCase.Issue resumes a stopped run on its own and retries an unavailable payment provider for up to 24 hours.
**Migration**: The 1-minute sweep is removed; Committed Checkouts at the time of the rollout are finished by the rollout task in this change.

### Requirement: A charged checkout left unissued is reported
**Reason**: OrderUseCase.Issue reports a charged Checkout to an admin when its retries end ("Charged but never issued").
**Migration**: None.
