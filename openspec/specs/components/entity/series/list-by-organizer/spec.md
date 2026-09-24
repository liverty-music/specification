# Series.ListByOrganizer

## Purpose

Lists every first-party Series an Organizer owns, newest first.

## Requirements

### Requirement: Organizer's series, newest first

ListByOrganizer SHALL return every Series the Organizer owns — DRAFT, PUBLISHED and CANCELLED — with its cover image, newest first; an Organizer with none SHALL yield an empty list, and a missing Organizer id SHALL fail with InvalidArgument.

#### Scenario: Mixed states
- **WHEN** the Organizer owns a DRAFT, a PUBLISHED and a CANCELLED Series
- **THEN** all three are returned, the most recently created first

#### Scenario: Missing organizer
- **WHEN** no Organizer id is given
- **THEN** ListByOrganizer fails with InvalidArgument
