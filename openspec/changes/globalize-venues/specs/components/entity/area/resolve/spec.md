## Purpose

Resolve finds the one first-level Area that a code or a name stands for, so text from any source (a search result, a map address, an admin's input, a fan's home) becomes the one code that Venues, Homes and reference areas compare.

## ADDED Requirements

### Requirement: A code or a name resolves to exactly one first-level Area

Resolve SHALL take a text and an optional country code and return one first-level Area. It SHALL trim spaces from the text and fail with InvalidArgument when nothing is left. A text in the form of an Area code, in any letter case, SHALL match the Area with that code in upper case. Any other text SHALL match an Area whose English name equals it with letter case ignored, or whose Japanese name equals it or equals it followed by 都, 道, 府 or 県; when a country code is given, only Areas of that country SHALL match a name. A region SHALL never match. Each matched Area SHALL lead to a first-level Area by following its replacement and then its parents. Resolve SHALL return that first-level Area when the matches lead to exactly one, and SHALL fail with NotFound when nothing matches or the matches lead to more than one first-level Area.

#### Scenario: First-level code

- **WHEN** Resolve is called with `JP-13`
- **THEN** it returns the Area `JP-13`

#### Scenario: Code in lower case

- **WHEN** Resolve is called with `us-ca`
- **THEN** it returns the Area `US-CA`

#### Scenario: Lower-level code

- **WHEN** Resolve is called with `FR-33`, whose parent is `FR-NAQ`
- **THEN** it returns the Area `FR-NAQ`

#### Scenario: Withdrawn code

- **WHEN** Resolve is called with `FR-75`, a code withdrawn for Paris and replaced by `FR-IDF`
- **THEN** it returns the Area `FR-IDF`

#### Scenario: Territory by either code

- **WHEN** Resolve is called with `HK` or with `CN-HK`
- **THEN** it returns the Area `HK` in both cases

#### Scenario: English name

- **WHEN** Resolve is called with `california`
- **THEN** it returns the Area `US-CA`

#### Scenario: Japanese name with and without its suffix

- **WHEN** Resolve is called with `愛知県` or with `東京`
- **THEN** it returns the Area `JP-23` or `JP-13`

#### Scenario: Region code

- **WHEN** Resolve is called with `JP-KANTO`
- **THEN** it fails with NotFound

#### Scenario: Region name

- **WHEN** Resolve is called with 関東, the name of the region `JP-KANTO` only
- **THEN** it fails with NotFound

#### Scenario: Well-formed code that is no Area

- **WHEN** Resolve is called with `JP-99`
- **THEN** it fails with NotFound

#### Scenario: Name without its diacritics

- **WHEN** Resolve is called with `Cordoba` and the Area's English name is `Córdoba`
- **THEN** it fails with NotFound

#### Scenario: Empty text

- **WHEN** Resolve is called with a text of only spaces
- **THEN** it fails with InvalidArgument

### Requirement: A name shared by two Areas needs to be narrowed to one

When a name matches Areas that lead to more than one first-level Area, Resolve SHALL fail with NotFound, unless a country code is given that leaves matches leading to exactly one first-level Area. Two first-level Areas of the same country with the same name SHALL fail with NotFound even with the country code.

#### Scenario: Shared name without a country

- **WHEN** Resolve is called with `Victoria`, the name of `AU-VIC` and of `MT-45`, and no country code
- **THEN** it fails with NotFound

#### Scenario: Shared name with a country

- **WHEN** Resolve is called with `Victoria` and country code `AU`
- **THEN** it returns the Area `AU-VIC`

#### Scenario: Same name twice in one country

- **WHEN** two first-level Areas of one country share a name and Resolve is called with that name and that country code
- **THEN** it fails with NotFound
