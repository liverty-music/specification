## ADDED Requirements

### Requirement: Two-Layer Vocabulary Model
The system SHALL classify every user-facing term into one of two layers based on whether the term corresponds to a protobuf entity definition.

#### Scenario: Term refers to a protobuf entity
- **WHEN** a user-facing term refers to a concept that is defined as a protobuf message, enum, or enum value in `specification/proto/`
- **THEN** the term SHALL be managed under Layer A (entity-grounded labels)
- **AND** its label SHALL live in the frontend i18n JSON under the `entity.*` namespace

#### Scenario: Term has no entity backing
- **WHEN** a user-facing term is a coined brand expression, marketing phrase, lane name, or product noun that has no corresponding protobuf entity
- **THEN** the term SHALL be managed under Layer B (brand expressions)
- **AND** its canonical JA and EN forms SHALL be listed in `openspec/specs/brand-vocabulary/spec.md`

#### Scenario: Layer B term becomes entity-modeled
- **WHEN** a Layer B term is later modeled as a protobuf entity
- **THEN** the term SHALL be migrated to Layer A
- **AND** the corresponding row SHALL be removed from this spec's brand expression table

---

### Requirement: Asymmetric Locale Labels
The system SHALL allow JA and EN entries under the same `entity.*` key to use different surface words, treating asymmetric localization as a normal i18n choice rather than a defect.

#### Scenario: HypeLevel surfaces differently per locale
- **WHEN** the `HypeLevel` enum is rendered in the UI
- **THEN** `entity.hype.label` in `ja/translation.json` MAY be `"Stage"`
- **AND** `entity.hype.label` in `en/translation.json` MAY be `"Hype"`
- **AND** neither value is required to match the protobuf enum name

#### Scenario: Lint accepts asymmetric values
- **WHEN** the brand-vocabulary lint script runs against an `entity.*` key whose JA and EN values differ in meaning (not just spelling)
- **THEN** the script SHALL NOT flag the difference as an error

---

### Requirement: Brand Expression Registry
The system SHALL maintain a single registry table in this spec listing every Layer B brand expression with its canonical JA and EN forms.

#### Scenario: Initial registry contents
- **WHEN** this spec is first introduced
- **THEN** the registry SHALL include the following Layer B expressions:
  - `Personal timetable promise` — JA: `あなただけのタイムテーブル` / EN: `your personal timetable`
  - `HOME STAGE lane` — JA: `HOME STAGE` / EN: `HOME STAGE`
  - `NEAR STAGE lane` — JA: `NEAR STAGE` / EN: `NEAR STAGE`
  - `AWAY STAGE lane` — JA: `AWAY STAGE` / EN: `AWAY STAGE`

#### Scenario: Adding a new brand expression
- **WHEN** a new coined phrase is introduced into user-facing copy
- **AND** the phrase has no corresponding protobuf entity
- **THEN** a row SHALL be added to this spec's registry table before or alongside the change that introduces the phrase

#### Scenario: Removing a graduated expression
- **WHEN** a Layer B expression becomes entity-modeled and is migrated to Layer A
- **THEN** its row SHALL be removed from this spec's registry table in the same change that performs the migration
