## MODIFIED Requirements

### Requirement: The place named like the listed venue, otherwise the most relevant

Venue.SelectPlace SHALL pick, among the places a search returned for a listed venue name (most relevant first) that count for the venue's admin area, the first place whose canonical name is the same listed venue as the listed name (see Venue, "Same listed venue"); when no counted place has such a name, it SHALL pick the most relevant counted place. The places whose first-level Area equals the venue's admin area count; when no place has that Area, the places in the admin area's country whose first-level Area is unknown count instead. A place whose first-level Area is another Area, or whose country is unknown, does not count. When no admin area is given, every place counts. It SHALL pick no place when no place counts.

#### Scenario: A less relevant place has the listed name
- **WHEN** the listed name is "Zepp Haneda" and the places are "羽田空港第3ターミナル駅" first and "ZEPP HANEDA" second
- **THEN** "ZEPP HANEDA" is picked

#### Scenario: No place has the listed name
- **WHEN** the listed name is "日本武道館" and the places are "Nippon Budokan" first and "北の丸公園" second
- **THEN** "Nippon Budokan" is picked

#### Scenario: No place
- **WHEN** the search returned no place
- **THEN** no place is picked

#### Scenario: A place of the same name elsewhere
- **WHEN** the admin area is US-CA and the places named "The Independent" are one in JP-27 first and one in US-CA second
- **THEN** the place in US-CA is picked

#### Scenario: Every place is elsewhere
- **WHEN** the admin area is JP-13 and every place lies in another admin area
- **THEN** no place is picked

#### Scenario: A place whose area is unknown counts by its country
- **WHEN** the admin area is US-CA and the only place is in the United States with an unknown first-level Area
- **THEN** that place is picked

#### Scenario: A place in the area beats one known only by country
- **WHEN** the admin area is US-CA and the places named "The Independent" are one in the United States with an unknown first-level Area first and one in US-CA second
- **THEN** the place in US-CA is picked

#### Scenario: A place whose country is unknown
- **WHEN** the admin area is US-CA and the only place has no country
- **THEN** no place is picked
