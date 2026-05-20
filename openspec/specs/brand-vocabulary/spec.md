## Purpose

Manage the canonical vocabulary used in user-facing copy across Liverty Music while preserving the protobuf entity layer as the authoritative ubiquitous-language source. Classify each term into one of two layers — entity-grounded labels (Layer A, surfaced through a dedicated `entity.*` i18n namespace mirroring protobuf entity names) or brand expressions without entity backing (Layer B, catalogued in this spec) — so terminology drift cannot occur silently and JA/EN locales may legitimately choose asymmetric surface labels for the same entity.

## Requirements

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

### Requirement: Entity Namespace Mirrors Protobuf Names
The system SHALL derive `entity.*` i18n key paths from protobuf entity names using a mechanical lower-camelCase rule.

#### Scenario: Enum entity with Level suffix
- **WHEN** the protobuf type is an enum named with a trailing `Level` suffix (e.g. `HypeLevel`)
- **THEN** the i18n namespace SHALL be `entity.<lowerCamelStem>` where `<lowerCamelStem>` is the enum name with the `Level` suffix removed and the first character lowercased (e.g. `entity.hype`)
- **AND** the entity's display name SHALL live at `entity.<stem>.label`
- **AND** each enum value SHALL live at `entity.<stem>.values.<lowerCamelValue>`

#### Scenario: Plain entity message
- **WHEN** the protobuf type is a message named without a special suffix (e.g. `Concert`, `Artist`)
- **THEN** the i18n namespace SHALL be `entity.<lowerCamelName>` (e.g. `entity.concert`, `entity.artist`)
- **AND** the entity's display name SHALL live at `entity.<lowerCamelName>.label`

#### Scenario: Nested entity field
- **WHEN** an entity field is itself a domain concept worth surfacing (e.g. `User.HomeArea`)
- **THEN** the i18n namespace SHALL be `entity.<lowerCamelFieldName>` (e.g. `entity.homeArea`)

---

### Requirement: Asymmetric Locale Labels
The system SHALL allow JA and EN entries under the same `entity.*` key to use different surface words, treating asymmetric localization as a normal i18n choice rather than a defect.

#### Scenario: Lint accepts asymmetric values
- **WHEN** the brand-vocabulary lint script runs against an `entity.*` key whose JA and EN values differ in meaning (not just spelling)
- **THEN** the script SHALL NOT flag the difference as an error

---

### Requirement: Entity Namespace Locale Parity
The system SHALL ensure that every `entity.*` key path declared in one locale's translation file also exists in the other locale's translation file.

#### Scenario: Missing key in EN locale
- **WHEN** `entity.hype.values.watch` exists in `ja/translation.json`
- **AND** `entity.hype.values.watch` does not exist in `en/translation.json`
- **THEN** the lint script SHALL report a missing-key error and exit non-zero

#### Scenario: Missing key in JA locale
- **WHEN** `entity.concert.label` exists in `en/translation.json`
- **AND** `entity.concert.label` does not exist in `ja/translation.json`
- **THEN** the lint script SHALL report a missing-key error and exit non-zero

---

### Requirement: Entity Name Validation
The system SHALL verify that each `entity.*` second-segment key corresponds to a known protobuf entity name (or a documented exception).

#### Scenario: Unknown entity stem
- **WHEN** an i18n entry uses `entity.<unknown>` where `<unknown>` is not present in the curated entity name list maintained by the lint script
- **THEN** the lint script SHALL report an unknown-entity warning that includes the offending key path
- **AND** the lint script SHALL exit non-zero unless the stem is added to the curated list

#### Scenario: Curated list is the contract
- **WHEN** a new protobuf entity is added that needs a UI label
- **THEN** the entity stem SHALL be added to the lint script's curated entity name list as part of the same change

---

### Requirement: Brand Expression Registry
The system SHALL maintain a single registry table in this spec listing every Layer B brand expression with its canonical JA and EN forms.

#### Scenario: Initial registry contents
- **WHEN** this spec is interpreted at the current revision
- **THEN** the registry SHALL include the following Layer B expressions, each with identical JA and EN surface forms unless otherwise noted:
  - `Personal timetable promise` — JA: `あなただけのタイムテーブル` / EN: `your personal timetable`
  - `HOME STAGE lane` — JA: `HOME STAGE` / EN: `HOME STAGE`
  - `NEAR STAGE lane` — JA: `NEAR STAGE` / EN: `NEAR STAGE`
  - `AWAY STAGE lane` — JA: `AWAY STAGE` / EN: `AWAY STAGE`
  - `Hype concept label` — JA: `Hype` / EN: `Hype`
  - `Hype tier — Watch` — JA: `Watch` / EN: `Watch`
  - `Hype tier — Home` — JA: `Home` / EN: `Home`
  - `Hype tier — Nearby` — JA: `Nearby` / EN: `Nearby`
  - `Hype tier — Away` — JA: `Away` / EN: `Away`

#### Scenario: Adding a new brand expression
- **WHEN** a new coined phrase is introduced into user-facing copy
- **AND** the phrase has no corresponding protobuf entity
- **THEN** a row SHALL be added to this spec's registry table before or alongside the change that introduces the phrase

#### Scenario: Removing a graduated expression
- **WHEN** a Layer B expression becomes entity-modeled and is migrated to Layer A
- **THEN** its row SHALL be removed from this spec's registry table in the same change that performs the migration

#### Scenario: Japanese gloss is prose, not label
- **WHEN** a Japanese-locale help or descriptive sentence introduces a Layer B brand expression that may be unfamiliar to first-time JA readers (e.g. `Hype`)
- **THEN** the sentence MAY include a parenthetical gloss (e.g. `Hype（熱量）`) inline within the prose
- **AND** the gloss SHALL NOT be promoted to the canonical surface label or stored as a separate i18n key

---

### Requirement: Hype Tier Surface Labels Are Layer B
The system SHALL treat the four hype tier surface labels (`Watch`, `Home`, `Nearby`, `Away`) and the Hype concept label itself as Layer B brand expressions rendered invariantly across JA and EN locales, NOT as Layer A entity-grounded labels.

#### Scenario: Hype tier label is invariant English
- **WHEN** any UI surface (help sheet, table column header, slider legend, prose) renders a hype tier label
- **THEN** the surface form SHALL be one of `Watch`, `Home`, `Nearby`, `Away` regardless of the active locale
- **AND** the surface form SHALL NOT be sourced from an `entity.hype.values.*` i18n key
- **AND** the JA-only tier translations (`観測`, `地元`, `近郊`, `全国`) SHALL NOT appear anywhere in user-facing copy

#### Scenario: Hype concept label is invariant English
- **WHEN** any UI surface labels the four-tier concept itself (e.g. as a column-group label, a help sheet section title prefix, an accessibility name)
- **THEN** the surface form SHALL be `Hype` regardless of the active locale
- **AND** the surface form SHALL NOT be sourced from an `entity.hype.label` i18n key
- **AND** the JA-only concept label `Stage` SHALL NOT appear as a label for the Hype concept

#### Scenario: Lint script does not enforce parity on Hype keys
- **WHEN** the brand-vocabulary lint script processes the translation files
- **THEN** the script SHALL NOT require `entity.hype.label` or `entity.hype.values.*` to exist in either locale
- **AND** the script SHALL flag any newly-introduced `entity.hype.*` key as a vocabulary-layer violation (Layer A namespace used for what is now a Layer B concept)

---

### Requirement: Lint Script Integration
The system SHALL run the brand-vocabulary lint script as part of the frontend's `make lint` target so that violations block CI.

#### Scenario: Lint passes during normal build
- **WHEN** the frontend `make lint` target is invoked
- **AND** all `entity.*` keys satisfy parity and known-entity rules
- **THEN** the lint script SHALL exit zero
- **AND** `make lint` SHALL continue to its remaining checks

#### Scenario: Lint fails on missing parity
- **WHEN** the frontend `make lint` target is invoked
- **AND** an `entity.*` key violates locale parity or references an unknown entity stem
- **THEN** the lint script SHALL print the violating key path with the offending file
- **AND** the lint script SHALL exit non-zero
- **AND** `make lint` SHALL fail
