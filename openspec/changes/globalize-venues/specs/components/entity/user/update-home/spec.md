## REMOVED Requirements

### Requirement: UpdateHome creates or replaces the home as a whole

**Reason**: A Home is owned by its User and has no id of its own to keep, and level 2 is removed.
**Migration**: "UpdateHome sets the home's area" states the behavior without a Home id or level 2.

### Requirement: UpdateHome sets the home's centroid

**Reason**: A Home no longer stores a centroid of its own; it has its Area's current reference point.
**Migration**: "UpdateHome sets the home's area" states what the returned Home carries; the User entity's "A Home's reference point is its Area's" states the rule.

## ADDED Requirements

### Requirement: UpdateHome sets the home's area

UpdateHome SHALL make the User's Home the first-level Area that the supplied level 1 names, whether or not the User had a Home, store the change completely or not at all, and return the updated User. The returned Home SHALL carry that code as level 1, the Area's country as country code, and the Area's reference point when it has one. When the supplied level 1 is not the code of a first-level Area, UpdateHome SHALL fail with InvalidArgument and leave the User's Home unchanged.

#### Scenario: First home

- **WHEN** UpdateHome runs for a User with no Home, with level 1 `JP-13`
- **THEN** the User's Home is `JP-13` and the returned User carries it with the reference point of the Area `JP-13`

#### Scenario: Changing the home

- **WHEN** UpdateHome runs for a User whose Home is `JP-13`, with level 1 `KR-11`
- **THEN** the User's Home is `KR-11`, the User has no other Home, and the returned Home carries country code `KR` and the reference point of the Area `KR-11`

#### Scenario: Level 1 that is no first-level Area

- **WHEN** UpdateHome runs for a User whose Home is `JP-13`, with level 1 `JP-99`
- **THEN** UpdateHome fails with InvalidArgument and the User's Home is still `JP-13`
