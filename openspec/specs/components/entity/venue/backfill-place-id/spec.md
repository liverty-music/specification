# Venue.BackfillPlaceID

## Purpose

Gives an existing Venue that has no place id the place id it was later resolved to.

## Requirements

### Requirement: Fill only a missing place id

BackfillPlaceID SHALL set the Venue's place id only when the Venue has none. When the Venue already has a place id, or another Venue already holds the given place id, it SHALL change nothing and succeed.

#### Scenario: Missing place id filled
- **WHEN** the Venue has no place id
- **THEN** it takes the given place id

#### Scenario: Existing place id kept
- **WHEN** the Venue already has place id P1 and P2 is given
- **THEN** the Venue keeps P1

#### Scenario: Place id held elsewhere
- **WHEN** another Venue already holds the given place id
- **THEN** the call succeeds and nothing changes
