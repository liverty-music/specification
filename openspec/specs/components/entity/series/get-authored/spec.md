# Series.GetAuthored

## Purpose

Returns a Series with its performances and performers as its organizer authored them: DraftEvents and draft performers while DRAFT, Events and their performers afterwards.

## Requirements

### Requirement: Draft or live content by state

GetAuthored SHALL return the Series with its cover image and, while it is DRAFT, its DraftEvents and draft performers; otherwise its Events and the Artists performing at them. Performances SHALL be ordered by date, then start time with unknown start times last. It SHALL fail with NotFound when no Series has the id.

#### Scenario: Draft series
- **WHEN** a DRAFT Series with two DraftEvents is read
- **THEN** its two DraftEvents are returned as its performances

#### Scenario: Published series
- **WHEN** a PUBLISHED Series is read
- **THEN** its Events are returned as its performances

#### Scenario: Unknown id
- **WHEN** no Series has the id
- **THEN** GetAuthored fails with NotFound
