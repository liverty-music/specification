## ADDED Requirements

### Requirement: The place named like the listed venue, otherwise the most relevant

Venue.SelectPlace SHALL pick, among the places a search returned for a listed venue name (most relevant first), the first place whose canonical name is the same listed venue as the listed name (see Venue, "Same listed venue"); when no place has such a name, it SHALL pick the most relevant place. It SHALL pick no place when the search returned none.

#### Scenario: A less relevant place has the listed name
- **WHEN** the listed name is "Zepp Haneda" and the places are "羽田空港第3ターミナル駅" first and "ZEPP HANEDA" second
- **THEN** "ZEPP HANEDA" is picked

#### Scenario: No place has the listed name
- **WHEN** the listed name is "日本武道館" and the places are "Nippon Budokan" first and "北の丸公園" second
- **THEN** "Nippon Budokan" is picked

#### Scenario: No place
- **WHEN** the search returned no place
- **THEN** no place is picked
