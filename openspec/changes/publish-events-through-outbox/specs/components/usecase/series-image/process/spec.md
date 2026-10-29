## ADDED Requirements

### Requirement: Runs for each uploaded SeriesImage

Process SHALL run for each SeriesImage announced as uploaded by SeriesImage.Create, with that SeriesImage and its Series. A transient failure SHALL cause the same SeriesImage to be processed again; every step SHALL be safe to repeat, so an announcement delivered twice leaves one processed cover. When the SeriesImage no longer exists, nothing SHALL be processed.

#### Scenario: SeriesImage uploaded
- **WHEN** SeriesImage.Create announces a SeriesImage uploaded for Series S
- **THEN** Process runs for that SeriesImage and Series S

#### Scenario: Delivered twice
- **WHEN** the same upload announcement is delivered twice
- **THEN** the Series has one cover made from that SeriesImage

#### Scenario: SeriesImage gone
- **WHEN** the SeriesImage no longer exists (SeriesImage.Get NotFound)
- **THEN** nothing is processed

#### Scenario: Storage briefly unavailable
- **WHEN** reading the original upload fails
- **THEN** the SeriesImage is processed again later

## REMOVED Requirements

### Requirement: Triggered by an upload announcement
**Reason**: The upload is now announced by SeriesImage.Create together with the stored SeriesImage, which carries its Series (components/entity/series-image/create), instead of by SeriesUseCase.SetCoverImage after it.
**Migration**: Replaced by "Runs for each uploaded SeriesImage".
