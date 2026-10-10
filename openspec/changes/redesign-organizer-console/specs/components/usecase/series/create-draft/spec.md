## ADDED Requirements

### Requirement: Each event's venue is a picked place

Every event SHALL give the place id of a place the operator picked from the map catalog; an event without one SHALL fail CreateDraft with InvalidArgument, storing nothing. For each event, CreateDraft SHALL use the Venue holding the place id when one is held (Venue.GetByPlaceID). Otherwise it SHALL read the place from the map catalog (Venue.GetPlace) and create a Venue with the place id and the place's name, coordinates and admin area (Venue.Create). When the catalog cannot be reached it SHALL fail with Unavailable, storing nothing; when the catalog has no such place it SHALL fail with InvalidArgument, storing nothing.

#### Scenario: Known place id
- **WHEN** an event gives a place id that a Venue holds
- **THEN** that Venue is used and the catalog is not read

#### Scenario: New place
- **WHEN** an event gives the place id of Zepp Haneda and no Venue holds it
- **THEN** a Venue for Zepp Haneda is created with that place id, its coordinates and the admin area JP-13

#### Scenario: Same name in two cities
- **WHEN** one event picks CLUB QUATTRO in Shibuya and another picks CLUB QUATTRO in Umeda
- **THEN** the two events have two different Venues, in JP-13 and JP-27

#### Scenario: Venue typed but not picked
- **WHEN** an event gives a venue name but no place id
- **THEN** CreateDraft fails with InvalidArgument and nothing is stored

#### Scenario: Catalog down for a new place
- **WHEN** no Venue holds the given place id and the catalog cannot be reached
- **THEN** CreateDraft fails with Unavailable and nothing is stored

## REMOVED Requirements

### Requirement: Each event's venue is found or created

**Reason**: A typed venue name with no place id created a Venue keyed by that name and no admin area, so same-named halls in different cities merged into one Venue and new Venues had no coordinates. Every event now gives a place picked from the map catalog.

**Migration**: Replaced by "Each event's venue is a picked place". Existing Venues are kept; only new drafts and new event rows must give a place id.

