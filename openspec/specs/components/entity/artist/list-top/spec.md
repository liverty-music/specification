# Artist.ListTop

## Purpose

Looks up the currently popular artists in the music catalog, for a genre tag, a country, or worldwide.

## Requirements

### Requirement: ListTop picks the chart from tag, then country, then worldwide
ListTop SHALL return the catalog's popular artists for the given tag when a tag is given, ignoring the country; otherwise for the given country when a country is given; otherwise worldwide. Results are in chart order, each with a name and, when the catalog knows it, an MBID. When the limit is greater than 0 it SHALL return at most that many artists; when the limit is 0 the catalog's default number applies (TODO(threshold)). When the chart is empty, ListTop SHALL return an empty list.

#### Scenario: Tag and country given
- **WHEN** ListTop is called with the tag "rock" and the country "Japan"
- **THEN** it returns the worldwide "rock" chart

#### Scenario: Country only
- **WHEN** ListTop is called with the country "Japan" and no tag
- **THEN** it returns the chart for Japan

#### Scenario: Neither given
- **WHEN** ListTop is called with no tag and no country
- **THEN** it returns the worldwide chart

#### Scenario: Limit given
- **WHEN** ListTop is called with a limit of 20
- **THEN** it returns at most 20 artists

### Requirement: ListTop reports an unknown country and catalog failures
ListTop SHALL fail with NotFound when the catalog rejects the given country, and with Unavailable when the catalog cannot be reached.

#### Scenario: Unknown country
- **WHEN** ListTop is called with a country the catalog does not recognize
- **THEN** ListTop fails with NotFound

#### Scenario: Catalog unreachable
- **WHEN** the catalog cannot be reached
- **THEN** ListTop fails with Unavailable
