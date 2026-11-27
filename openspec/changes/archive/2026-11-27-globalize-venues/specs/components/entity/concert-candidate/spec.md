## ADDED Requirements

### Requirement: A concert candidate keeps only the resolved place id from the map catalog

A ConcertCandidate SHALL carry, of what the map catalog returned for its venue, only the resolved place id, and only when its venue was resolved to a place; it SHALL carry no venue name, coordinates or admin area read from the map catalog. Its admin area, when present, SHALL be the subdivision code as discovered, which is resolved to a first-level Area only when the candidate is approved (a candidate staged earlier may carry a lower-level or unknown code such as FR-33 or JP-99), and its time zone, when present, SHALL be an IANA time zone name as discovered; a ConcertCandidate without an admin area SHALL have no time zone.

#### Scenario: Unresolved venue
- **WHEN** a ConcertCandidate was staged because its venue could not be resolved
- **THEN** it carries no resolved place id

#### Scenario: Resolved venue
- **WHEN** a ConcertCandidate was staged for a collision after its venue was resolved to place P, which the map catalog names "Zepp Haneda (TOKYO)"
- **THEN** it carries the resolved place id P and no venue name or coordinates from the map catalog

#### Scenario: Discovered area and time zone
- **WHEN** a ConcertCandidate is staged for an event discovered in JP-13 with the time zone Asia/Tokyo
- **THEN** it carries the admin area JP-13 and the time zone Asia/Tokyo

#### Scenario: Area kept as discovered
- **WHEN** a ConcertCandidate was staged with the admin area FR-33
- **THEN** it keeps FR-33 until it is approved

#### Scenario: Time zone without an area
- **WHEN** a ConcertCandidate has the time zone Asia/Tokyo and no admin area
- **THEN** it is invalid

## REMOVED Requirements

### Requirement: Resolved preview is all or nothing on the place

**Reason**: A ConcertCandidate no longer keeps a resolved venue name, coordinates or admin area from the map catalog, so there is no preview left to keep consistent.
**Migration**: "A concert candidate keeps only the resolved place id from the map catalog" states what a candidate carries; the resolved name, coordinates and admin area are dropped in this change's data migration, and approval reads the coordinates by place id.
