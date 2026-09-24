# Artist.ListByMBIDs

## Purpose

Returns the registered artists for a list of MBIDs, skipping MBIDs that are not registered.

## Requirements

### Requirement: ListByMBIDs returns known artists in input order
ListByMBIDs SHALL return the registered artist for each given MBID that is registered, in the order of the given MBIDs, and SHALL skip every MBID that is not registered without failing.

#### Scenario: Some MBIDs are known
- **WHEN** ListByMBIDs is called with MBIDs A, B and C and only C and A are registered
- **THEN** it returns the artists for A and C, in that order

#### Scenario: No MBID is known
- **WHEN** none of the given MBIDs is registered
- **THEN** it returns an empty list without error

#### Scenario: Empty input
- **WHEN** ListByMBIDs is called with no MBIDs
- **THEN** it returns an empty list without error
