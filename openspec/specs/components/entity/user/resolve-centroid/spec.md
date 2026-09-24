# User.ResolveCentroid

## Purpose

Looks up the approximate geographic centre of a Home's level 1 area, for a Home that does not carry its centroid.

## Requirements

### Requirement: Centroid of a supported level 1 area

ResolveCentroid SHALL return the centre of the Home's level 1 area when that area is in the supported catalog (the 47 Japanese prefectures), the same centre a stored Home of that area carries. For any other level 1 area, or when no Home is given, it SHALL fail and return no centroid.

#### Scenario: Japanese prefecture

- **WHEN** ResolveCentroid is called for a Home in JP-40
- **THEN** it returns the centre of Fukuoka

#### Scenario: Area outside the catalog

- **WHEN** ResolveCentroid is called for a Home in US-CA
- **THEN** it fails and returns no centroid
