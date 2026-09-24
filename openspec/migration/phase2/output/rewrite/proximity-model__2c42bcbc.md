<!-- spec: proximity-model | target: components/entity/concert | flags: CLASSNAME | new_name: Concert classifies its proximity to a user's home -->

### Requirement: Concert classifies its proximity to a user's home

The Go entity layer SHALL provide a `ProximityTo` receiver method on `Concert` that classifies the geographic relationship between the concert's venue and a user's home. This method SHALL be a pure function over entity fields with no infrastructure dependencies.

#### Scenario: HOME classification by admin_area match

- **WHEN** `Concert.ProximityTo(home)` is called
- **AND** the concert's venue `admin_area` matches `home.Level1`
- **THEN** the method SHALL return `ProximityHome`

#### Scenario: NEARBY classification by Haversine distance

- **WHEN** `Concert.ProximityTo(home)` is called
- **AND** the venue's `admin_area` does not match `home.Level1`
- **AND** the venue has latitude and longitude coordinates
- **AND** the Haversine distance between `(home.Latitude, home.Longitude)` and the venue coordinates is less than or equal to 200km
- **THEN** the method SHALL return `ProximityNearby`

#### Scenario: AWAY classification for distant venues

- **WHEN** `Concert.ProximityTo(home)` is called
- **AND** the Haversine distance exceeds 200km
- **THEN** the method SHALL return `ProximityAway`

#### Scenario: AWAY classification when venue has no coordinates

- **WHEN** `Concert.ProximityTo(home)` is called
- **AND** the venue's latitude or longitude is nil
- **THEN** the method SHALL return `ProximityAway`

#### Scenario: AWAY classification when home is nil

- **WHEN** `Concert.ProximityTo(nil)` is called
- **THEN** the method SHALL return `ProximityAway`

#### Scenario: AWAY classification when venue is nil

- **WHEN** `Concert.ProximityTo(home)` is called
- **AND** the concert's venue is nil
- **THEN** the method SHALL return `ProximityAway`
