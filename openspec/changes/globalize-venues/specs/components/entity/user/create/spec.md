## REMOVED Requirements

### Requirement: Create sets the home's centroid

**Reason**: A Home no longer stores a centroid of its own, and the 47 Japanese prefectures are no longer the only areas with one: a Home has its Area's current reference point, for every Area that has one.
**Migration**: "A created Home names its Area" states what Create stores and returns; the User entity's "A Home's reference point is its Area's" states the rule.

## ADDED Requirements

### Requirement: A created Home names its Area

When Create stores a Home, it SHALL store the Home as the code of its first-level Area, owned by the new User. The returned User's Home SHALL carry that code as level 1, the Area's country as country code, and the Area's reference point when it has one. When the supplied Home's level 1 is not the code of a first-level Area, Create SHALL fail with InvalidArgument and store no User.

#### Scenario: Japanese prefecture

- **WHEN** Create stores a Home with country code `JP` and level 1 `JP-13`
- **THEN** the returned Home carries country code `JP`, level 1 `JP-13` and the reference point of the Area `JP-13`

#### Scenario: Area without a reference point

- **WHEN** Create stores a Home whose Area has no reference point
- **THEN** the returned Home carries its country code and level 1 and no reference point

#### Scenario: Level 1 that is no first-level Area

- **WHEN** Create runs with a Home of level 1 `FR-33`
- **THEN** Create fails with InvalidArgument and no User is stored
