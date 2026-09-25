# Spec Delta

## MODIFIED Requirements

### Requirement: Search reports failures

ArtistUseCase.Search SHALL return the errors of Artist.Search, Artist.ListByMBIDs, and Artist.Create unchanged, preserving each port's failure code rather than replacing it with Internal.

#### Scenario: Catalog unavailable

- **WHEN** Artist.Search fails with Unavailable
- **THEN** Search fails with Unavailable

#### Scenario: Catalog rate-limited

- **WHEN** Artist.Search fails with ResourceExhausted
- **THEN** Search fails with ResourceExhausted

#### Scenario: Catalog request timed out

- **WHEN** Artist.Search fails with DeadlineExceeded
- **THEN** Search fails with DeadlineExceeded
