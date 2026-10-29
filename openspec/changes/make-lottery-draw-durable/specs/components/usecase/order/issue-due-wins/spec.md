## REMOVED Requirements

### Requirement: Issue within one minute after the draw
**Reason**: OrderUseCase.Issue runs once for each Won entry and resumes on its own after a stop, so no sweep is needed.
**Migration**: The 1-minute sweep is removed with the method. Before the rollout, Won entries whose Order is Pending are listed in prod; none is expected (design "Migration Plan").
