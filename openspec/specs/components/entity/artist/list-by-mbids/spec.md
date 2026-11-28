# Artist.ListByMBIDs

## Purpose

Returns the registered artists for a list of MBIDs, skipping MBIDs that are not registered.

## Requirements

### Requirement: ListByMBIDs returns known artists in input order
ListByMBIDs SHALL return the registered artist for each given MBID that is registered, whether as the artist's MBID or among its other_mbids, once per artist, in the order of the first given MBID that finds each artist, and SHALL skip every MBID that is not registered without failing.

#### Scenario: Some MBIDs are known
- **WHEN** ListByMBIDs is called with MBIDs A, B and C and only C and A are registered
- **THEN** it returns the artists for A and C, in that order

#### Scenario: No MBID is known
- **WHEN** none of the given MBIDs is registered
- **THEN** it returns an empty list without error

#### Scenario: Empty input
- **WHEN** ListByMBIDs is called with no MBIDs
- **THEN** it returns an empty list without error

#### Scenario: Replaced MBID
- **WHEN** an artist was corrected from MBID A to MBID B and ListByMBIDs is called with A
- **THEN** it returns that artist

#### Scenario: Two MBIDs of one artist
- **WHEN** ListByMBIDs is called with MBIDs A and B of one artist, A being an other MBID
- **THEN** it returns that artist once
