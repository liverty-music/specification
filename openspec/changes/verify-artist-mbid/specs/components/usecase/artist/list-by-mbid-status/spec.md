## Purpose

ArtistUseCase.ListByMBIDStatus returns the registered artists in one mbid_status, so an admin sees the Ambiguous artists waiting for a choice.

## ADDED Requirements

### Requirement: ListByMBIDStatus returns the artists in that status
ArtistUseCase.ListByMBIDStatus SHALL take an mbid_status and return the artists Artist.ListByMBIDStatus returns for it, in that order, and SHALL return its error unchanged.

#### Scenario: Ambiguous artists listed
- **WHEN** ListByMBIDStatus is called with Ambiguous and two artists are Ambiguous
- **THEN** both are returned, the one registered first listed first

#### Scenario: Store unavailable
- **WHEN** Artist.ListByMBIDStatus fails with Unavailable
- **THEN** ListByMBIDStatus fails with Unavailable
