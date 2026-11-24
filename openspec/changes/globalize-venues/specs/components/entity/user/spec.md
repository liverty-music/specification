## REMOVED Requirements

### Requirement: Home validation

**Reason**: A Home's level 1 is now the code of a first-level Area, which a well-formed code alone does not guarantee (`JP-99`), and a territory without subdivisions (`HK`) is now a valid level 1. Level 2 is removed: no client ever set it and no Home carries one.
**Migration**: "A Home names a first-level Area" states the rule. A level 2 sent by an older client is not accepted by the request shape and is never stored.

## ADDED Requirements

### Requirement: A Home names a first-level Area

A Home SHALL be valid only when its country code is two uppercase letters and its level 1 is the code of a first-level Area of that country. A Home SHALL have no other area than level 1. Any other Home SHALL be invalid.

#### Scenario: Prefecture

- **WHEN** a Home has country code `JP` and level 1 `JP-13`
- **THEN** it is valid

#### Scenario: Territory without subdivisions

- **WHEN** a Home has country code `HK` and level 1 `HK`
- **THEN** it is valid

#### Scenario: Malformed country code

- **WHEN** a Home has country code `j` or `jp`
- **THEN** it is invalid

#### Scenario: Not an Area code

- **WHEN** a Home has level 1 `INVALID`
- **THEN** it is invalid

#### Scenario: Level 1 in another country

- **WHEN** a Home has country code `JP` and level 1 `US-CA`
- **THEN** it is invalid

#### Scenario: Well-formed code that is no Area

- **WHEN** a Home has country code `JP` and level 1 `JP-99`
- **THEN** it is invalid

#### Scenario: Lower-level Area

- **WHEN** a Home has country code `FR` and level 1 `FR-33`, whose parent is `FR-NAQ`
- **THEN** it is invalid

#### Scenario: Region

- **WHEN** a Home has country code `JP` and level 1 `JP-KANTO`
- **THEN** it is invalid

### Requirement: A Home's reference point is its Area's

A Home's reference point, the home area's centroid from which NEARBY distances are measured, SHALL be the current reference point of the Area its level 1 names, and the Home SHALL have none when that Area has none. A Home SHALL keep no reference point of its own: when the Area's reference point changes, every Home of that Area SHALL have the new one.

#### Scenario: Prefecture with a reference point

- **WHEN** a Home has level 1 `JP-40`
- **THEN** its reference point is the reference point of the Area `JP-40` (Fukuoka)

#### Scenario: Area without a reference point

- **WHEN** a Home's Area has no reference point
- **THEN** the Home has no reference point

#### Scenario: Area's reference point changed

- **WHEN** the reference point of the Area `KR-11` changes after a User set a Home of `KR-11`
- **THEN** that User's Home has the new reference point
