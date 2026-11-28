# Spec Delta

## MODIFIED Requirements

### Requirement: Only cancellable events of the series

CancelEvents SHALL take the current time and fail with FailedPrecondition, changing nothing, when a given Event is not an Event of the Series, is already CANCELLED, or is PUBLISHED and not cancellable at that time; with NotFound when the Series does not exist; and with InvalidArgument when no Event is given.

#### Scenario: Already cancelled
- **WHEN** a given Event is CANCELLED
- **THEN** CancelEvents fails with FailedPrecondition and nothing changes

#### Scenario: Concert already held
- **WHEN** a given PUBLISHED Event started 30 hours ago
- **THEN** CancelEvents fails with FailedPrecondition and nothing changes

#### Scenario: Unknown series
- **WHEN** no Series has the id
- **THEN** CancelEvents fails with NotFound
