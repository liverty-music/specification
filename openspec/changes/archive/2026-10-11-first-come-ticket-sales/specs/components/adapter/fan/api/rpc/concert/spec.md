# Spec Delta

## MODIFIED Requirements

### Requirement: What a returned concert carries

Every response of the fan concert service that returns Concerts SHALL also return, once each, every Series and every Artist those Concerts refer to; a Concert carries only the id of its Series (through its Event) and the ids of its Artists. Every returned Venue SHALL carry its id, name and admin area, and never its coordinates. When there are no concerts, List SHALL return an empty list, not NotFound. Every returned Series SHALL carry its Organizer when it is first-party, so the fan app can tell first-party concerts from discovered ones and show who sells the tickets: the Organizer's id, name and, when present, seller details, which the checkout shows as the 特商法 (Specified Commercial Transactions Act) disclosure, and never its platform fee rate. Every returned Series SHALL carry its description, cover image, visibility and publish state when it has them, on every call alike. A Series' share token SHALL never be returned.

#### Scenario: Venue without coordinates

- **WHEN** a returned Concert's Venue has known coordinates
- **THEN** the response carries the Venue's id, name and admin area and no coordinates

#### Scenario: Artist without concerts

- **WHEN** List is called for an artist with no concerts
- **THEN** it returns an empty list

#### Scenario: First-party concert in a list

- **WHEN** ListByFollower returns a Concert whose Series belongs to an Organizer
- **THEN** the Series returned with it carries that Organizer's id

#### Scenario: Discovered concert in a list

- **WHEN** ListByFollower returns a Concert whose Series has no organizer
- **THEN** the Series returned with it carries no Organizer id

#### Scenario: Tour in one list

- **WHEN** ListByFollower returns three Concerts of one Series, all performed by the same Artist
- **THEN** the response carries that Series once and that Artist once

#### Scenario: Cover image in a list

- **WHEN** ListByArtists returns a Concert whose first-party Series has a cover image
- **THEN** the Series returned with it carries the cover image, as Get does

#### Scenario: Seller shown for a first-party concert

- **WHEN** Get returns a Concert whose Series belongs to an Organizer with seller details and a platform fee rate
- **THEN** the Series returned with it carries the Organizer's id, name and seller details, and no platform fee rate
