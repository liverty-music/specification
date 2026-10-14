# Spec Delta

## MODIFIED Requirements

### Requirement: Same validation as a new draft

Update SHALL reject unrepresented performers with PermissionDenied and invalid input with InvalidArgument exactly as Create does, except that the date of a PUBLISHED or CANCELLED Event is not checked against the current day. Each new or DRAFT event SHALL give the place id of a picked place, failing with InvalidArgument and changing nothing without one, and its Venue SHALL be found or created from that place as Create does. A PUBLISHED or CANCELLED Event SHALL NOT need a place id: its venue counts as unchanged when the given venue name equals its listed venue name and, when a place id is given and its Venue has one, the two place ids are equal, so a date published before venues were picked from the map catalog can still be corrected.

#### Scenario: Doors after start
- **WHEN** an updated event opens after it starts
- **THEN** Update fails with InvalidArgument

#### Scenario: Correcting a past published date
- **WHEN** a PUBLISHED Event dated yesterday is given unchanged with a new open time
- **THEN** Update does not fail for the date

#### Scenario: Published date without a place id
- **WHEN** the owner corrects the title of a Series whose PUBLISHED Event's Venue has no place id, giving that Event without a place id
- **THEN** the title is changed and the Event keeps its Venue

#### Scenario: New date without a place id
- **WHEN** the owner adds an event without an id and without a place id
- **THEN** Update fails with InvalidArgument and nothing changes
