## ADDED Requirements

### Requirement: An artist is found by its known names
An Artist's known_names SHALL hold its name and every alias the music catalog gives for it, each in normalized form and each once. The normalized form of a name is the name with its compatibility forms unified (Unicode NFKC), its letters lowercased, its surrounding white space removed and each inner run of white space made one space. An Artist is known by a name when the name's normalized form is among its known_names.

#### Scenario: Letter case and width
- **WHEN** an artist's known names are derived from the name `Ｓａｕｃｙ　Dog`
- **THEN** they hold `saucy dog`, and the artist is known by `Saucy dog`

#### Scenario: Alias
- **WHEN** an artist named `ヨルシカ` has the catalog alias `Yorushika`
- **THEN** it is known by `yorushika` and by `ヨルシカ`

#### Scenario: Same name twice
- **WHEN** an alias differs from the name only in letter case
- **THEN** known_names holds it once

#### Scenario: Part of a name
- **WHEN** an artist's only name is `tomoo kosugi`
- **THEN** it is not known by `tomoo`
