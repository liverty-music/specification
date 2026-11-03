## REMOVED Requirements

### Requirement: Stalled checkouts finished within one minute
**Reason**: OrderUseCase.Issue resumes a stopped run on its own and tries an unavailable payment provider again, so no sweep is needed.
**Migration**: The 1-minute sweep is removed. Before the rollout, Committed Checkouts are listed in prod; none is expected (design "Migration Plan").

### Requirement: A charged checkout left unissued is reported
**Reason**: An OrderUseCase.Issue that has not ended within 24 hours stops and is reported for an admin like every workflow that cannot finish (components/infrastructure/backend/process/durable-workflows).
**Migration**: None.
