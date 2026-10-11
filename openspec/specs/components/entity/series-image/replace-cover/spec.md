# SeriesImage.ReplaceCover

## Purpose

Makes a SeriesImage the cover of a Series in one step and returns the SeriesImage it replaced.

## Requirements

### Requirement: Atomic cover switch

ReplaceCover SHALL make the given SeriesImage the Series' cover and remove the previous cover SeriesImage, together or not at all, and SHALL return the previous cover's id, or none when the Series had no cover. When the given SeriesImage is already the cover it SHALL change nothing and return none. It SHALL fail with NotFound when the Series does not exist.

#### Scenario: Replace a cover
- **WHEN** the Series' cover is M1 and M2 is cut over
- **THEN** M2 is the cover, M1 is removed, and M1's id is returned

#### Scenario: Repeated cut-over
- **WHEN** M2 is already the cover and M2 is cut over again
- **THEN** nothing changes and no id is returned

#### Scenario: Series gone
- **WHEN** the Series does not exist
- **THEN** ReplaceCover fails with NotFound
