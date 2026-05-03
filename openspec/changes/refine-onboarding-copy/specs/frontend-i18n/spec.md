## ADDED Requirements

### Requirement: Legacy Key Removal After Entity Migration

When a top-level i18n namespace is superseded by an `entity.*` namespace path, the legacy keys SHALL be removed from both `ja/translation.json` and `en/translation.json` in the same change that introduces the `entity.*` replacements.

#### Scenario: hype.* migrated to entity.hype.*

- **WHEN** `entity.hype.label` and `entity.hype.values.{watch,home,nearby,away}` are populated in both locales
- **AND** all template / TypeScript bindings are switched to read from `entity.hype.*`
- **THEN** the legacy `hype.watch`, `hype.home`, `hype.nearby`, `hype.away` keys SHALL be removed from both locale files
- **AND** no source file SHALL retain a reference to a removed legacy key (verified by Biome / typecheck against generated i18n key types if available, otherwise by grep in CI)

#### Scenario: Per-screen hype labels collapse into the entity path

- **WHEN** a screen-local key (e.g. `myArtists.table.watch`, `myArtists.hypeExplanation.watch`, `myArtists.table.home`) duplicates a value now expressible via `entity.hype.values.*` or `entity.hype.label`
- **THEN** the screen template SHALL bind to the `entity.*` path instead
- **AND** the duplicate screen-local key SHALL be removed from both locale files
- **AND** any wording variation in the screen-local key (e.g. `近郊まで` vs `近郊`, `どこでも！` vs `全国`) SHALL be reconciled in favor of the canonical `entity.hype.values.*` value, eliminating the variant
