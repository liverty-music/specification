## ADDED Requirements

### Requirement: An artist is found by its name keys
A name key SHALL be a name with its compatibility forms unified (Unicode NFKC), its letters lowercased, its surrounding white space removed and each inner run of white space made one space. An Artist's name_keys SHALL hold the key of its name and the key of every alias the music catalog gives for it, each once. An Artist has a name when the name's key is among its name_keys.

#### Scenario: Letter case and width
- **WHEN** an artist's name keys are derived from the name `Ｓａｕｃｙ　Dog`
- **THEN** they hold `saucy dog`, and the artist has the name `Saucy dog`

#### Scenario: Alias
- **WHEN** an artist named `ヨルシカ` has the catalog alias `Yorushika`
- **THEN** it has the name `yorushika` and the name `ヨルシカ`

#### Scenario: Same key twice
- **WHEN** an alias differs from the name only in letter case
- **THEN** name_keys holds the key once

#### Scenario: Part of a name
- **WHEN** an artist's only name is `tomoo kosugi`
- **THEN** it does not have the name `tomoo`
