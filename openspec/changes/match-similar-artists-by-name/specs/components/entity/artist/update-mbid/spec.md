## ADDED Requirements

### Requirement: UpdateMBID stores the known names of the artist it names
UpdateMBID SHALL take the known names of the artist the given MBID names and replace the artist's known_names with them, adding the stored name when it is missing, in the same change as the MBID, name and status: all are stored or none.

#### Scenario: Corrected artist
- **WHEN** UpdateMBID replaces a namesake's MBID, with the right artist's known names
- **THEN** the artist is found by those names and no longer by the namesake's aliases

#### Scenario: Refused change
- **WHEN** UpdateMBID fails with AlreadyExists
- **THEN** the artist keeps its known_names
