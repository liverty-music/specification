## REMOVED Requirements

### Requirement: Empty series is removed

**Reason**: Removing the ConcertCandidate's emptied Series right after the rejection raced with writes to that Series. An empty Series row is harmless for a day.
**Migration**: Replaced by SeriesUseCase.RemoveEmptyDiscovered ("Empty discovered Series are removed daily").
