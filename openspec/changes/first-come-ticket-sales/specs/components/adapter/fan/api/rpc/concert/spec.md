# Spec Delta

## MODIFIED Requirements

### Requirement: What a returned concert carries

The Venue of every Concert returned by the fan boundary SHALL carry its id, name and admin area, and never its coordinates. A concert preview returned by SearchNewConcerts SHALL carry no Venue. When there are no concerts, List SHALL return an empty list, not NotFound. The Series of every returned Concert SHALL carry its Organizer when it is first-party, so the fan app can tell first-party concerts from discovered ones and show who sells the tickets: the Organizer's id, name and, when present, seller details, which the checkout shows as the 特商法 (Specified Commercial Transactions Act) disclosure, and never its platform fee rate. The Series SHALL carry its description, cover image, visibility and publish state when it has them. A Series' share token SHALL never be returned.

#### Scenario: Venue without coordinates

- **WHEN** a returned Concert's Venue has known coordinates
- **THEN** the response carries the Venue's id, name and admin area and no coordinates

#### Scenario: Artist without concerts

- **WHEN** List is called for an artist with no concerts
- **THEN** it returns an empty list

#### Scenario: First-party concert in a list

- **WHEN** ListByFollower returns a Concert whose Series belongs to an Organizer
- **THEN** the Concert's Series carries that Organizer's id

#### Scenario: Discovered concert in a list

- **WHEN** ListByFollower returns a Concert whose Series has no organizer
- **THEN** the Concert's Series carries no Organizer id

#### Scenario: Seller shown for a first-party concert

- **WHEN** Get returns a Concert whose Series belongs to an Organizer with seller details and a platform fee rate
- **THEN** the Concert's Series carries the Organizer's id, name and seller details, and no platform fee rate
