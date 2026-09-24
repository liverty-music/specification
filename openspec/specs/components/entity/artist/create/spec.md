# Artist.Create

## Purpose

Registers one or more artists by MBID and returns the registered artist for each, whether it was new or already known.

## Requirements

### Requirement: Create registers each MBID once
Create SHALL register every given artist whose MBID is not yet registered and SHALL return, for each given artist in input order, the registered artist with that MBID. An artist whose MBID is already registered SHALL be returned as registered, unchanged, and SHALL NOT be registered a second time. A new artist SHALL keep the id it was given, or get a fresh id when it has none.

#### Scenario: New MBID
- **WHEN** Create is called with an artist whose MBID is not registered
- **THEN** the artist is registered and returned

#### Scenario: Known MBID
- **WHEN** Create is called with an artist whose MBID is already registered under another name
- **THEN** the already registered artist is returned with its existing id and name, and nothing new is registered

#### Scenario: Mixed input keeps order
- **WHEN** Create is called with a known artist followed by a new artist
- **THEN** the result lists the known artist first and the new artist second

#### Scenario: Empty input
- **WHEN** Create is called with no artists
- **THEN** it returns an empty list and registers nothing

### Requirement: Create rejects an artist without a valid MBID
Create SHALL fail with InvalidArgument and register nothing when any given artist has no MBID or an MBID that is not 36 characters long.

#### Scenario: Artist without MBID
- **WHEN** Create is called with two artists and one has no MBID
- **THEN** Create fails with InvalidArgument and neither artist is registered

#### Scenario: Malformed MBID
- **WHEN** Create is called with an artist whose MBID is not 36 characters long
- **THEN** Create fails with InvalidArgument and nothing is registered

### Requirement: Create is all or nothing
Create SHALL register all of the new artists in one call or none of them; any other failure SHALL be reported as Internal or Unavailable.

#### Scenario: Store failure
- **WHEN** the artists cannot be stored
- **THEN** Create fails and none of the new artists is registered
