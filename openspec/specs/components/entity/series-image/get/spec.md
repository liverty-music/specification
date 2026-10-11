# SeriesImage.Get

## Purpose

Returns one SeriesImage by id.

## Requirements

### Requirement: Find by id

Get SHALL return the SeriesImage with its Organizer and variant addresses, and SHALL fail with NotFound when none exists.

#### Scenario: Unknown series image
- **WHEN** no SeriesImage has the id
- **THEN** Get fails with NotFound
