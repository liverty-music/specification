## ADDED Requirements

### Requirement: UpdateMBID stores the name keys of the artist it names
UpdateMBID SHALL take the name keys of the artist the given MBID names and replace the artist's name_keys with them, adding the key of the stored name when it is missing, in the same change as the MBID, name and status: all are stored or none.

#### Scenario: Corrected artist
- **WHEN** UpdateMBID replaces a namesake's MBID, with the right artist's name keys
- **THEN** the artist is found by those names and no longer by the namesake's aliases

#### Scenario: Refused change
- **WHEN** UpdateMBID fails with AlreadyExists
- **THEN** the artist keeps its name_keys
