# components/entity/media/list-by-organizer Specification

## Purpose
Media.ListByOrganizer returns every Media record an Organizer owns, whether or not a Series currently uses it as its cover.

## Requirements

### Requirement: ListByOrganizer returns the Organizer's Media

ListByOrganizer SHALL return every Media record owned by the given Organizer, including Media that no Series uses as its cover, and SHALL return an empty list when the Organizer owns none.

#### Scenario: Cover and replaced upload

- **WHEN** the Organizer owns a Media used as a cover and a Media no Series uses
- **THEN** both are returned

#### Scenario: No media

- **WHEN** the Organizer owns no Media
- **THEN** an empty list is returned
