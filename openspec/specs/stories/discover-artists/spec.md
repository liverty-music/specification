# Discover Artists

## Purpose

A fan finds artists to follow by searching by name, browsing popular charts or exploring artists similar to one they know; every artist found is a registered artist that soon shows the catalog's canonical name and its community images, and charts and similar artists suggest only artists whose activity has not ended.

```mermaid
usecase-beta
direction LR
actor Fan("fan")
systemBoundary "Liverty Music"
  Goal("Discover artists")
  ArtistUseCaseSearch("ArtistUseCase.Search")
  ArtistUseCaseListTop("ArtistUseCase.ListTop")
  ArtistUseCaseListSimilar("ArtistUseCase.ListSimilar")
  ArtistUseCaseCreate("ArtistUseCase.Create")
  ArtistUseCaseRefresh("ArtistUseCase.Refresh")
  ArtistImageSyncUseCaseSyncArtistImage("ArtistImageSyncUseCase.SyncArtistImage")
end
Fan --> Goal
Goal ..> : include ArtistUseCaseSearch
Goal ..> : include ArtistUseCaseListTop
Goal ..> : include ArtistUseCaseListSimilar
Goal ..> : include ArtistUseCaseCreate
Goal ..> : include ArtistUseCaseRefresh
Goal ..> : include ArtistImageSyncUseCaseSyncArtistImage
```

## Requirements

### Requirement: A discovered artist is registered and enriched
When ArtistUseCase.Search, ArtistUseCase.ListTop or ArtistUseCase.ListSimilar returns an artist that was not registered before, the artist SHALL be registered at once and announced as created; the announcement SHALL run ArtistUseCase.Refresh and ArtistImageSyncUseCase.SyncArtistImage for it, so that the artist then carries the catalog's canonical name, whether its activity has ended, and its images.

#### Scenario: Newly discovered artist
- **WHEN** a fan searches for a name and a result was not registered before
- **THEN** the result is returned as a registered artist, and after the announcement is handled the artist has the catalog's canonical name, its activity status and its images

#### Scenario: Already registered artist
- **WHEN** a chart lists an artist that is already registered
- **THEN** the registered artist is returned and no announcement is made for it

### Requirement: Artist images are kept current
An artist's images SHALL be checked again by the daily image run once its last check is more than 7 days old, while at least one fan follows the artist. An artist that nobody follows SHALL keep the images of its last check. An artist registered through ArtistUseCase.Create is announced by Artist.Create like any other registered artist, so its first image check follows that announcement.

#### Scenario: Stale images
- **WHEN** a followed artist's images were last checked 8 days ago
- **THEN** the next daily image run checks them again and records the result

#### Scenario: Artist nobody follows
- **WHEN** an artist found by a search had its images checked when it was registered, more than 7 days ago, and nobody follows it
- **THEN** the daily image run does not check its images again

#### Scenario: Artist followed later
- **WHEN** a fan follows an artist whose images were last checked 30 days ago
- **THEN** the next daily image run checks them again and records the result

#### Scenario: Artist registered directly
- **WHEN** an artist is registered through ArtistUseCase.Create
- **THEN** its images are first checked once its announcement is handled

### Requirement: Charts and similar artists do not suggest artists whose activity has ended
ArtistUseCase.ListTop and ArtistUseCase.ListSimilar SHALL leave out artists whose activity_ended is true, so the artists a fan is offered to follow from a chart or from an artist they know are artists that may still perform. ArtistUseCase.Search SHALL still return an artist whose activity_ended is true, so a fan who looks an artist up by name finds it. ArtistUseCase.Refresh SHALL keep activity_ended in line with the music catalog: an artist is read when it is registered and again at least once every 30 days, whether or not anyone follows it. A hiatus is not an ended activity: an artist on hiatus is still suggested.

#### Scenario: Dissolved group in the chart
- **WHEN** a dissolved group whose activity_ended is true is in the Japan chart
- **THEN** the chart returned by ArtistUseCase.ListTop does not include it

#### Scenario: Name search for a dissolved group
- **WHEN** a fan searches for the name of a group whose activity_ended is true
- **THEN** ArtistUseCase.Search returns the group

#### Scenario: Group dissolves after it was registered
- **WHEN** a registered group that nobody follows is marked as dissolved in the catalog
- **THEN** within 30 days a daily run sets its activity_ended to true, and ArtistUseCase.ListTop and ArtistUseCase.ListSimilar leave it out from then on

#### Scenario: Ended artist found for the first time
- **WHEN** ArtistUseCase.ListSimilar registers an artist whose activity the catalog marks as ended
- **THEN** that call returns it, and once its announcement is handled the next call leaves it out
