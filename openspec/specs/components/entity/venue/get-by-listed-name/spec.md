# Venue.GetByListedName

## Purpose

Returns the Venue first stored under a given listed venue name and admin area.

## Requirements

### Requirement: Exact listed name and admin area

GetByListedName SHALL return the Venue whose listed venue name equals the given name exactly — case and whitespace included — and whose admin area equals the given one, where an absent admin area matches only an absent admin area. It SHALL fail with NotFound when there is none.

#### Scenario: Match
- **WHEN** a Venue lists "日本武道館" in JP-13 and that pair is given
- **THEN** GetByListedName returns it

#### Scenario: Different case misses
- **WHEN** a Venue lists "Zepp Haneda" and "zepp haneda" is given with the same admin area
- **THEN** GetByListedName fails with NotFound

#### Scenario: Absent admin area matches absent only
- **WHEN** a Venue lists "Club X" with no admin area and "Club X" is given with JP-13
- **THEN** GetByListedName fails with NotFound
