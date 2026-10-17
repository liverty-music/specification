## MODIFIED Requirements

### Requirement: ListTop reuses a recent result
ArtistUseCase.ListTop SHALL return the earlier result, without consulting the catalog, when the same country, tag and limit were answered within the last 6 hours.

#### Scenario: Repeated call
- **WHEN** ListTop is called twice with the same country, tag and limit 10 minutes apart
- **THEN** the second call returns the first call's result without a catalog lookup

#### Scenario: Result older than 6 hours
- **WHEN** ListTop is called with the same country, tag and limit more than 6 hours after the last such call
- **THEN** the catalog is consulted again
