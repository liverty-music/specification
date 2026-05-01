## Why

Liverty Music's user-facing copy has accumulated terminology drift: `ライブ` and `コンサート` coexist for the same concept, the dashboard is referred to interchangeably as `ダッシュボード`, `タイムテーブル`, or `ライブカレンダー`, and the concept of expressing fan intensity is split between `Hype` (proto `HypeLevel`) and `熱量` (used in spotlight copy). At the same time, brand-coined expressions like `あなただけのタイムテーブル` and `HOME STAGE / NEAR STAGE / AWAY STAGE` carry meaningful product identity but have no managed home.

Two competing temptations are wrong:
- **Add labels to protobuf entities directly** would mix presentation concerns into the schema layer and force EN/JA symmetry where localization rightly allows asymmetry (e.g., `HypeLevel` will surface as `Hype` in EN but `Stage` in JA — a normal i18n choice, not an entity-language problem).
- **Maintain a parallel "brand glossary"** would create a third source of truth that drifts from both proto definitions and the i18n JSON.

We need a structured separation that preserves protobuf entities as the conceptual source of truth, the i18n JSON as the locale-specific label source of truth, and a small focused document for brand expressions that have no entity backing.

## What Changes

- **Establish a two-layer vocabulary model**:
  - **Layer A (entity-grounded labels)**: i18n keys for entity surface labels live under a new `entity.*` namespace in `frontend/src/locales/{ja,en}/translation.json`, mirroring the protobuf entity name (e.g. `entity.hype.label`, `entity.hype.values.watch`). JA and EN may choose asymmetric labels.
  - **Layer B (brand expressions without entity backing)**: maintained in a single new spec `openspec/specs/brand-vocabulary/spec.md` listing coined phrases and their JA/EN canonical forms.
- **Amend the i18n key naming convention** to recognize `entity.*` as a sibling namespace to the existing `<page>.<component>.<element>` pattern.
- **Add a CI lint script** in the frontend repo that verifies every `entity.*` key has parity in both locales and (best-effort) maps to a known protobuf entity name.
- **No existing copy is rewritten** in this change. Migration of the current `hype.*`, `dashboard.*`, etc. keys into the new model is deferred to the follow-up `refine-onboarding-copy` change.

## Capabilities

### New Capabilities
- `brand-vocabulary`: Defines the two-layer vocabulary model, the `entity.*` namespace conventions, the Layer B brand-expressions document format, and the lint rules that enforce parity.

### Modified Capabilities
- `frontend-i18n`: Adds the `entity.*` namespace as an additional permitted top-level key pattern alongside `<page>.<component>.<element>`. Existing requirements remain intact.

## Impact

- **specification repo**: new `openspec/specs/brand-vocabulary/spec.md` (created during apply). No protobuf changes.
- **frontend repo**: new top-level `entity` key in `src/locales/ja/translation.json` and `src/locales/en/translation.json` (initially empty / scaffolded). New `scripts/check-brand-vocabulary.ts` lint script wired into `make lint`.
- **No breaking API or BSR changes**. No backend changes.
- **Downstream**: the follow-up `refine-onboarding-copy` change consumes this infrastructure to migrate existing keys (notably `hype.*` → `entity.hype.*` with JA "Stage" / EN "Hype").
