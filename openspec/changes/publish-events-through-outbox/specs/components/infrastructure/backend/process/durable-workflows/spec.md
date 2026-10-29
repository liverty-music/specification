## REMOVED Requirements

### Requirement: An announcement from a workflow has one id
**Reason**: Every announcement, inside a workflow or not, gets one id when it is recorded with its fact (components/infrastructure/backend/process/event-delivery). A workflow step that runs again after its operation committed finds the change made and announces nothing.
**Migration**: The step-derived ids go; consumers keep treating a repeated id as one.
