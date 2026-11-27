## ADDED Requirements

### Requirement: Proximity of a venue to a home area

A Concert's proximity to a home area SHALL be classified, in this order: AWAY when there is no home area or no venue; HOME when the venue's admin area equals the home area's level-1 code; NEARBY when both the venue's coordinates and the home area's centroid are known and the great-circle distance between them is at most 200 km; AWAY otherwise.

#### Scenario: Same admin area is HOME
- **WHEN** the venue's admin area is JP-13 and the home area's level-1 code is JP-13
- **THEN** the proximity is HOME

#### Scenario: Admin area match wins over distance
- **WHEN** the venue's admin area equals the home area's level-1 code and the venue is 500 km from the centroid
- **THEN** the proximity is HOME

#### Scenario: Different admin area within 200 km is NEARBY
- **WHEN** the venue's admin area is JP-14, the home area's level-1 code is JP-13, and the venue is 30 km from the home area's centroid
- **THEN** the proximity is NEARBY

#### Scenario: Beyond 200 km is AWAY
- **WHEN** the admin areas differ and the venue is 500 km from the home area's centroid
- **THEN** the proximity is AWAY

#### Scenario: Venue coordinates unknown
- **WHEN** the admin areas differ and the venue has no coordinates
- **THEN** the proximity is AWAY

#### Scenario: Home centroid unknown
- **WHEN** the admin areas differ and the home area has no centroid
- **THEN** the proximity is AWAY

#### Scenario: No home area
- **WHEN** there is no home area
- **THEN** the proximity is AWAY

#### Scenario: No venue
- **WHEN** the Concert has no venue
- **THEN** the proximity is AWAY

## REMOVED Requirements

### Requirement: Proximity to a home area

**Reason**: Every Venue has a first-level admin area, so a venue without one can no longer be classified.

**Migration**: Replaced by "Proximity of a venue to a home area".
