## REMOVED Requirements

### Requirement: Issue within one minute after the draw
**Reason**: OrderUseCase.Issue runs for each Won entry as soon as the draw records it and resumes on its own after a stop, so no sweep is needed.
**Migration**: The schedule is removed with the method; Won entries without an Order at the time of the rollout are issued by the rollout task in this change.
