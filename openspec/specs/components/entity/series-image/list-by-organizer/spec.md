# components/entity/series-image/list-by-organizer Specification

## Purpose
SeriesImage.ListByOrganizer returns every SeriesImage record an Organizer owns, whether or not a Series currently uses it as its cover.

## Requirements

### Requirement: ListByOrganizer returns the Organizer's SeriesImage

ListByOrganizer SHALL return every SeriesImage record owned by the given Organizer, including SeriesImage that no Series uses as its cover, and SHALL return an empty list when the Organizer owns none.

#### Scenario: Cover and replaced upload

- **WHEN** the Organizer owns a SeriesImage used as a cover and a SeriesImage no Series uses
- **THEN** both are returned

#### Scenario: No series image

- **WHEN** the Organizer owns no SeriesImage
- **THEN** an empty list is returned
