## MODIFIED Requirements

### Requirement: Search reuses a recent result
ArtistUseCase.Search SHALL return the earlier result, without consulting the catalog or registering anything, when the same query was answered within the last 6 hours.

#### Scenario: Repeated query
- **WHEN** Search is called twice with the same query 10 minutes apart
- **THEN** the second call returns the first call's result without a catalog lookup

#### Scenario: Result older than 6 hours
- **WHEN** Search is called with the same query more than 6 hours after the last such call
- **THEN** the catalog is consulted again
