## ADDED Requirements

### Requirement: Runs for each recorded processing request

Process SHALL run for each processing request recorded by SeriesImage.Create, with that SeriesImage and the Series the request names. A transient failure SHALL cause the same SeriesImage to be processed again; every step SHALL be safe to repeat, so a request delivered twice leaves one processed cover. When the SeriesImage no longer exists, nothing SHALL be processed.

#### Scenario: SeriesImage uploaded
- **WHEN** SeriesImage.Create records a request to process a SeriesImage for Series S
- **THEN** Process runs for that SeriesImage and Series S

#### Scenario: Delivered twice
- **WHEN** the same processing request is delivered twice
- **THEN** the Series has one cover made from that SeriesImage

#### Scenario: SeriesImage gone
- **WHEN** the SeriesImage no longer exists (SeriesImage.Get NotFound)
- **THEN** nothing is processed

#### Scenario: Storage briefly unavailable
- **WHEN** reading the original upload fails
- **THEN** the SeriesImage is processed again later

## REMOVED Requirements

### Requirement: Triggered by an upload announcement
**Reason**: The processing request is now recorded by SeriesImage.Create together with the stored SeriesImage (components/entity/series-image/create), instead of published by SeriesUseCase.SetCoverImage after it.
**Migration**: Replaced by "Runs for each recorded processing request".
