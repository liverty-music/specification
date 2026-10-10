## MODIFIED Requirements

### Requirement: ResolveOfficialSiteURL reports catalog failures
ResolveOfficialSiteURL SHALL fail with NotFound when the catalog has no artist for the MBID, with Unavailable when the catalog cannot be reached, and with Internal for an unexpected catalog response.

#### Scenario: Catalog unreachable
- **WHEN** the catalog cannot be reached
- **THEN** ResolveOfficialSiteURL fails with Unavailable

#### Scenario: MBID unknown to the catalog
- **WHEN** the catalog has no artist for the MBID, as for an MBID removed from the catalog or one the catalog never had
- **THEN** ResolveOfficialSiteURL fails with NotFound
