# Media.CutOverSeriesMedia

## Purpose

Makes a Media the cover of a Series in one step and returns the Media it replaced.

## Requirements

### Requirement: Atomic cover switch

CutOverSeriesMedia SHALL make the given Media the Series' cover and remove the previous cover Media, together or not at all, and SHALL return the previous cover's id, or none when the Series had no cover. When the given Media is already the cover it SHALL change nothing and return none. It SHALL fail with NotFound when the Series does not exist.

#### Scenario: Replace a cover
- **WHEN** the Series' cover is M1 and M2 is cut over
- **THEN** M2 is the cover, M1 is removed, and M1's id is returned

#### Scenario: Repeated cut-over
- **WHEN** M2 is already the cover and M2 is cut over again
- **THEN** nothing changes and no id is returned

#### Scenario: Series gone
- **WHEN** the Series does not exist
- **THEN** CutOverSeriesMedia fails with NotFound
