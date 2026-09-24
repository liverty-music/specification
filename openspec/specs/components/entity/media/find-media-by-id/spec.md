# Media.FindMediaByID

## Purpose

Returns one Media by id.

## Requirements

### Requirement: Find by id

FindMediaByID SHALL return the Media with its Organizer, kind and attributes, and SHALL fail with NotFound when none exists.

#### Scenario: Unknown media
- **WHEN** no Media has the id
- **THEN** FindMediaByID fails with NotFound
