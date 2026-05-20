## MODIFIED Requirements

### Requirement: Asymmetric Locale Labels
The system SHALL allow JA and EN entries under the same `entity.*` key to use different surface words, treating asymmetric localization as a normal i18n choice rather than a defect.

#### Scenario: Lint accepts asymmetric values
- **WHEN** the brand-vocabulary lint script runs against an `entity.*` key whose JA and EN values differ in meaning (not just spelling)
- **THEN** the script SHALL NOT flag the difference as an error

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

## ADDED Requirements

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

## REMOVED Requirements

### Requirement: HypeLevel surfaces differently per locale (scenario)
**Reason**: The asymmetric-locale scenario for `HypeLevel` permitted `entity.hype.label` to be `Stage` in JA and `Hype` in EN. This change unifies the surface form to invariant English (`Hype`) and graduates the four tier values from Layer A to Layer B. The scenario is no longer valid because the keys it referenced (`entity.hype.label`, `entity.hype.values.*`) no longer exist.

**Migration**: Frontend i18n files SHALL remove the `entity.hype.*` subtree. Any test or lint assertion that referenced `entity.hype.label` SHALL be updated to assert the invariant English `Hype` brand expression instead, or removed if it was specifically testing locale-asymmetry tolerance.

Note: the broader "Asymmetric Locale Labels" requirement is RETAINED (other future `entity.*` keys may still legitimately use asymmetric values); only the specific `HypeLevel` example scenario is removed.
