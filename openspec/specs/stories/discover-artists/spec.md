# Discover Artists

## Purpose

A fan finds artists to follow by searching by name, browsing popular charts or exploring artists similar to one they know; every artist found is a registered artist that soon shows the catalog's canonical name and its community images.

## Requirements

### Requirement: A discovered artist is registered and enriched
When ArtistUseCase.Search, ArtistUseCase.ListTop or ArtistUseCase.ListSimilar returns an artist that was not registered before, the artist SHALL be registered at once and announced as created; the announcement SHALL run ArtistNameResolutionUseCase.ResolveCanonicalName and ArtistImageSyncUseCase.SyncArtistImage for it, so that the artist then carries the catalog's canonical name, its images and, when it has a logo, its logo color profile.

#### Scenario: Newly discovered artist
- **WHEN** a fan searches for a name and a result was not registered before
- **THEN** the result is returned as a registered artist, and after the announcement is handled the artist has the catalog's canonical name and its images

#### Scenario: Already registered artist
- **WHEN** a chart lists an artist that is already registered
- **THEN** the registered artist is returned and no announcement is made for it

### Requirement: Artist images are kept current
An artist's images SHALL be checked again by the daily image run once its last check is more than 7 days old, and an artist registered through ArtistUseCase.Create, which makes no announcement, SHALL get its first image check from the daily image run.

#### Scenario: Stale images
- **WHEN** an artist's images were last checked 8 days ago
- **THEN** the next daily image run checks them again and records the result

#### Scenario: Artist registered directly
- **WHEN** an artist is registered through ArtistUseCase.Create
- **THEN** its images are first checked by the next daily image run
