## MODIFIED Requirements

### Requirement: List followed artists from backend
The `ArtistDiscoveryService.listFollowedFromBackend` method SHALL use the instance's `artistClient` to fetch followed artists from the backend.

#### Scenario: Fetching followed artists
- **WHEN** `listFollowedFromBackend` is called
- **THEN** it SHALL call `this.artistClient.listFollowed()` (not the unscoped `artistClient` variable)

#### Scenario: Bug fix verification
- **WHEN** a test calls `listFollowedFromBackend`
- **THEN** it SHALL NOT throw a `ReferenceError` for undefined `artistClient`
