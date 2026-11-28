## MODIFIED Requirements

### Requirement: Create registers each MBID once
Create SHALL take artists each with a name, a listening MBID, an MBID (the listening MBID unless a verification corrected it), an mbid_status and, for a Verified artist, its activity status, register every given artist none of whose two MBIDs is the mbid or listening_mbid of a registered artist, and SHALL return, for each given artist in input order, the registered artist found under either of its MBIDs. An artist found under an MBID SHALL be returned as registered, unchanged, and SHALL NOT be registered a second time. A new artist SHALL keep the id it was given, or get a fresh id when it has none, and SHALL be registered with the given listening MBID as its listening_mbid, the given MBID as its mbid, the given mbid_status and the given activity status.

#### Scenario: New MBID
- **WHEN** Create is called with an artist whose MBID is not registered
- **THEN** the artist is registered and returned

#### Scenario: Known MBID
- **WHEN** Create is called with an artist whose MBID is already registered under another name
- **THEN** the already registered artist is returned with its existing id and name, and nothing new is registered

#### Scenario: Replaced MBID
- **WHEN** Create is called with an artist whose listening MBID A is the listening_mbid of a registered artist whose mbid is B
- **THEN** that registered artist is returned and nothing new is registered or announced

#### Scenario: Corrected MBID already registered
- **WHEN** Create is called with listening MBID A, not registered, and MBID B, the mbid of a registered artist
- **THEN** that registered artist is returned and nothing new is registered or announced

#### Scenario: Registered with a verified MBID
- **WHEN** Create is called with listening MBID A, MBID B and mbid_status Verified, and neither MBID is registered
- **THEN** an artist with listening_mbid A, mbid B and mbid_status Verified is registered and returned

#### Scenario: Mixed input keeps order
- **WHEN** Create is called with a known artist followed by a new artist
- **THEN** the result lists the known artist first and the new artist second

#### Scenario: Empty input
- **WHEN** Create is called with no artists
- **THEN** it returns an empty list and registers nothing

### Requirement: Create rejects an artist without a valid MBID
Create SHALL fail with InvalidArgument and register nothing when any given artist has no MBID or no listening MBID, or one that is not 36 characters long.

#### Scenario: Artist without MBID
- **WHEN** Create is called with two artists and one has no MBID
- **THEN** Create fails with InvalidArgument and neither artist is registered

#### Scenario: Malformed MBID
- **WHEN** Create is called with an artist whose MBID is not 36 characters long
- **THEN** Create fails with InvalidArgument and nothing is registered

#### Scenario: Malformed listening MBID
- **WHEN** Create is called with an artist whose listening MBID is not 36 characters long
- **THEN** Create fails with InvalidArgument and nothing is registered
