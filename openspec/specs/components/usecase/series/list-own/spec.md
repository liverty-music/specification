# List Own

## Purpose

ListOwn returns every concert — Series with its performances and performers — authored by the caller's Organizer: drafts, published and cancelled, newest first.

## Requirements

### Requirement: Organizer's own series

ListOwn SHALL return the caller's Organizer's Series newest first (Series.ListByOrganizer), each with its performances and performers as authored (Series.GetAuthored), and only that Organizer's Series. A failure to read any one Series SHALL fail ListOwn.

#### Scenario: Drafts included
- **WHEN** the Organizer owns a DRAFT and a PUBLISHED Series
- **THEN** both are returned, each with its performances

#### Scenario: Cancelled included
- **WHEN** the Organizer owns a CANCELLED Series
- **THEN** it is returned

#### Scenario: Other organizers excluded
- **WHEN** another Organizer owns a Series
- **THEN** it is not returned

#### Scenario: Missing organizer
- **WHEN** no Organizer is given
- **THEN** ListOwn fails with InvalidArgument
