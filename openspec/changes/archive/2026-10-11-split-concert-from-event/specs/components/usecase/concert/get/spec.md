## MODIFIED Requirements

### Requirement: Concert with an event page

Get SHALL take an Event id and read the Concert with Concert.ListByIDs, with its Venue, performers and Series, the Series including its description, cover image, visibility and publish state. When the Series has an event page (see Series), Get SHALL return the Concert with that Series. Get needs no signed-in caller.

#### Scenario: Published public concert

- **WHEN** Get is called for an Event of a PUBLISHED PUBLIC first-party Series
- **THEN** it returns the Concert with its Series' description, cover image and publish state PUBLISHED

#### Scenario: Cancelled series

- **WHEN** Get is called for an Event of a CANCELLED PUBLIC first-party Series
- **THEN** it returns the Concert with its Series' publish state CANCELLED

### Requirement: Read failures

When Concert.ListByIDs fails for any reason, Get SHALL fail with that error unchanged and return no Concert.

#### Scenario: Store unavailable

- **WHEN** Concert.ListByIDs fails with Unavailable
- **THEN** Get fails with Unavailable
