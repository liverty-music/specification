## MODIFIED Requirements

### Requirement: Create registers each MBID once
Create SHALL register every given artist whose MBID is not yet registered, as an artist's MBID or among its other_mbids, and SHALL return, for each given artist in input order, the registered artist with that MBID. An artist whose MBID is already registered SHALL be returned as registered, unchanged, and SHALL NOT be registered a second time. A new artist SHALL keep the id it was given, or get a fresh id when it has none.

#### Scenario: New MBID
- **WHEN** Create is called with an artist whose MBID is not registered
- **THEN** the artist is registered and returned

#### Scenario: Known MBID
- **WHEN** Create is called with an artist whose MBID is already registered under another name
- **THEN** the already registered artist is returned with its existing id and name, and nothing new is registered

#### Scenario: Replaced MBID
- **WHEN** Create is called with an artist whose MBID is among the other_mbids of a registered artist
- **THEN** that registered artist is returned and nothing new is registered or announced

#### Scenario: Mixed input keeps order
- **WHEN** Create is called with a known artist followed by a new artist
- **THEN** the result lists the known artist first and the new artist second

#### Scenario: Empty input
- **WHEN** Create is called with no artists
- **THEN** it returns an empty list and registers nothing
