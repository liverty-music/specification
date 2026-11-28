## Purpose

The catalog artist service as the admin console reaches it: an admin reads the music catalog's namesakes of a registered artist to choose its MBID. Every call requires a signed-in caller with the admin role.

## ADDED Requirements

### Requirement: ListByArtist returns an artist's namesake candidates

CatalogArtistService.ListByArtist, which only the admin console offers, SHALL take an ArtistId and fail with InvalidArgument, before any usecase runs, when it is missing or malformed. It SHALL run CatalogArtistUseCase.ListByArtist and return the CatalogArtists it returns, in its order; errors from the usecase SHALL be returned unchanged.

#### Scenario: Admin reads the candidates

- **WHEN** a signed-in admin calls ListByArtist for an artist whose name two catalog artists share
- **THEN** the two CatalogArtists are returned with their MBID, name, country, life span, disambiguation and official site

#### Scenario: Unknown artist

- **WHEN** CatalogArtistUseCase.ListByArtist fails with NotFound
- **THEN** ListByArtist fails with NotFound

#### Scenario: Guest reads candidates

- **WHEN** a caller who is not signed in calls ListByArtist
- **THEN** it fails with Unauthenticated and no usecase runs

#### Scenario: Non-admin reads candidates

- **WHEN** a signed-in caller without the admin role calls ListByArtist
- **THEN** it fails with PermissionDenied and no usecase runs
