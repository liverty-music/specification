## RENAMED Requirements

- FROM: `### Requirement: Charts and similar artists do not suggest artists whose activity has ended`
- TO: `### Requirement: Discovery offers only verified artists whose activity has not ended`

## MODIFIED Requirements

### Requirement: A discovered artist is registered and enriched
When ArtistUseCase.Search, ArtistUseCase.ListTop or ArtistUseCase.ListSimilar finds an artist that was not registered before, the artist SHALL be registered at once and announced as created. ArtistUseCase.Search SHALL verify the artist's MBID before registering it; ArtistUseCase.ListTop and ArtistUseCase.ListSimilar register it Unverified. The announcement SHALL run ArtistUseCase.VerifyMBID and ArtistImageSyncUseCase.SyncArtistImage for it, so that the artist then carries a verified MBID, the catalog's canonical name, whether its activity has ended, and its images.

#### Scenario: Newly discovered artist
- **WHEN** a fan searches for a name and a result with no namesake in the catalog was not registered before
- **THEN** the result is returned as a registered Verified artist with the catalog's canonical name and activity status, and after the announcement is handled it has its images

#### Scenario: Already registered artist
- **WHEN** a chart lists an artist that is already registered
- **THEN** the registered artist is returned when it is offered to fans, and no announcement is made for it

#### Scenario: Artist first found in a chart
- **WHEN** a chart lists an artist that was not registered before
- **THEN** it is registered Unverified and not returned, and once its announcement is handled and it is Verified, the next ListTop call returns it

### Requirement: Discovery offers only verified artists whose activity has not ended
ArtistUseCase.Search, ArtistUseCase.ListTop and ArtistUseCase.ListSimilar SHALL return only artists whose mbid_status is Verified and whose activity_ended is false, so every artist a fan is offered to follow is one concert search looks for and whose MBID was checked against its namesakes. An artist whose MBID is Ambiguous SHALL reach an admin: an error is logged, which alerts the owner, and the admin console's Artist MBIDs screen offers its namesakes until the admin chooses one with ArtistUseCase.CorrectMBID. ArtistUseCase.Refresh SHALL keep activity_ended in line with the music catalog: an artist is read when it is registered and again at least once every 30 days, whether or not anyone follows it. A hiatus is not an ended activity: an artist on hiatus is still offered.

#### Scenario: Dissolved group in the chart
- **WHEN** a dissolved group whose activity_ended is true is in the Japan chart
- **THEN** the chart returned by ArtistUseCase.ListTop does not include it

#### Scenario: Name search for a dissolved group
- **WHEN** a fan searches for the name of a group whose activity_ended is true
- **THEN** ArtistUseCase.Search does not return the group

#### Scenario: Group dissolves after it was registered
- **WHEN** a registered group that nobody follows is marked as dissolved in the catalog
- **THEN** within 30 days a daily run sets its activity_ended to true, and ArtistUseCase.Search, ArtistUseCase.ListTop and ArtistUseCase.ListSimilar leave it out from then on

#### Scenario: Ended artist found for the first time
- **WHEN** ArtistUseCase.Search finds an artist not registered before whose activity the catalog marks as ended
- **THEN** it is registered Verified with activity_ended true and that call does not return it

#### Scenario: Artist whose MBID is ambiguous
- **WHEN** a fan searches for a name that two catalog artists without an official homepage share, and the result was not registered before
- **THEN** the search does not return it, the owner is alerted, and the Artist MBIDs screen lists it with both namesakes

#### Scenario: Admin resolves an ambiguous artist
- **WHEN** an admin chooses one of an Ambiguous artist's namesakes on the Artist MBIDs screen
- **THEN** the artist is Verified with that MBID and the next search for its name returns it
