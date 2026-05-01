## MODIFIED Requirements

### Requirement: Translation Resource Files
The system SHALL maintain translation JSON files for each supported locale with identical key structures.

#### Scenario: Key parity between locales
- **WHEN** a translation key exists in `ja/translation.json`
- **THEN** the same key SHALL exist in `en/translation.json`
- **AND** missing keys in EN SHALL fall back to the JA value

#### Scenario: Page-keyed naming convention
- **WHEN** a new translation key is added under any top-level namespace other than `entity`
- **THEN** the key SHALL follow the pattern `<page>.<component>.<element>` (e.g., `welcome.hero.title`, `settings.language.label`)

#### Scenario: Entity-keyed naming convention
- **WHEN** a new translation key is added under the `entity` top-level namespace
- **THEN** the key SHALL follow the pattern `entity.<entityStem>.label` for an entity's display name
- **AND** enum value labels SHALL follow the pattern `entity.<entityStem>.values.<lowerCamelValue>`
- **AND** `<entityStem>` SHALL be derived from the protobuf entity name per the `brand-vocabulary` capability's mirroring rule

#### Scenario: Reserved top-level namespace
- **WHEN** a developer adds a top-level key named `entity`
- **THEN** the key SHALL be reserved exclusively for entity-grounded labels managed by the `brand-vocabulary` capability
- **AND** ad-hoc page-keyed strings SHALL NOT be placed under `entity.*`
