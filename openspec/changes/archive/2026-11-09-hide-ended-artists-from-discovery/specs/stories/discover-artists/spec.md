# Spec Delta

## MODIFIED Requirements

### Requirement: A discovered artist is registered and enriched
When ArtistUseCase.Search, ArtistUseCase.ListTop or ArtistUseCase.ListSimilar returns an artist that was not registered before, the artist SHALL be registered at once and announced as created; the announcement SHALL run ArtistUseCase.Refresh and ArtistImageSyncUseCase.SyncArtistImage for it, so that the artist then carries the catalog's canonical name, whether its activity has ended, and its images.

#### Scenario: Newly discovered artist
- **WHEN** a fan searches for a name and a result was not registered before
- **THEN** the result is returned as a registered artist, and after the announcement is handled the artist has the catalog's canonical name, its activity status and its images

#### Scenario: Already registered artist
- **WHEN** a chart lists an artist that is already registered
- **THEN** the registered artist is returned and no announcement is made for it

## ADDED Requirements

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
