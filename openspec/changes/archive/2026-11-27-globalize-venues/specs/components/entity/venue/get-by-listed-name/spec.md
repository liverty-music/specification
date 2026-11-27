## REMOVED Requirements

### Requirement: Exact listed name and admin area

**Reason**: Every Venue now has an admin area, so the rule that an absent admin area matches only an absent one has nothing left to match.
**Migration**: "Exact listed name and admin area, both given" states the behavior; a lookup without an admin area fails with InvalidArgument.

## ADDED Requirements

### Requirement: Exact listed name and admin area, both given

GetByListedName SHALL take a listed venue name and an admin area, fail with InvalidArgument when either is empty, and return the Venue whose listed venue name equals the given name exactly, case and whitespace included, and whose admin area equals the given one. It SHALL fail with NotFound when there is none.

#### Scenario: Match
- **WHEN** a Venue lists "日本武道館" in JP-13 and that pair is given
- **THEN** GetByListedName returns it

#### Scenario: Different case misses
- **WHEN** a Venue lists "Zepp Haneda" and "zepp haneda" is given with the same admin area
- **THEN** GetByListedName fails with NotFound

#### Scenario: Other admin area misses
- **WHEN** a Venue lists "Club X" in JP-13 and "Club X" is given with JP-27
- **THEN** GetByListedName fails with NotFound

#### Scenario: No admin area given
- **WHEN** "Club X" is given without an admin area
- **THEN** GetByListedName fails with InvalidArgument
