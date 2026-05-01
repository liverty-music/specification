## Context

Liverty Music maintains three artifacts that together define the words a user sees on screen:

1. **Protobuf entity definitions** (`specification/proto/liverty_music/entity/v1/*.proto`) — the authoritative source of domain concepts (`User`, `Concert`, `HypeLevel`, etc.). Per repo convention these double as the project's ubiquitous-language dictionary.
2. **Frontend i18n JSON** (`frontend/src/locales/{ja,en}/translation.json`) — currently uses a `<page>.<component>.<element>` key convention (per the existing `frontend-i18n` capability) and contains every user-facing string.
3. **Ad-hoc brand-coined phrases** (e.g. `あなただけのタイムテーブル`, `HOME STAGE / NEAR STAGE / AWAY STAGE`) — currently scattered across i18n keys with no organizing principle.

Three problems have surfaced from an onboarding-UX exploration:

- **Drift**: the same domain concept is named differently in different copy locations (`ライブ` vs `コンサート`, `ダッシュボード` vs `タイムテーブル` vs `ライブカレンダー`, `登録` vs `フォロー`).
- **Asymmetric localization is a feature, not a bug**: the `HypeLevel` entity will continue to be called "Hype" in EN (a loanword with established fan-culture meaning) but should surface as "Stage" in JA (reusing the existing brand-coined `HOME STAGE / NEAR STAGE / AWAY STAGE` lane vocabulary). Forcing entity-name symmetry would either break EN or force a misleading proto rename.
- **Brand expressions have no managed home**: phrases like `あなただけのタイムテーブル` carry product identity and recur across screens, but live as one-off i18n keys with no cross-reference.

This change establishes a structured separation that addresses all three without introducing a parallel "glossary" that drifts from both proto and i18n.

## Goals / Non-Goals

**Goals:**
- Define a clear two-layer ownership model: entities own concepts, i18n owns labels, with a small dedicated doc owning brand-only phrases.
- Make the JA/EN asymmetry of `HypeLevel` (and any future entity) a normal, documented case rather than a one-off hack.
- Provide CI-enforced parity guarantees for the new `entity.*` namespace so labels can't silently drift between locales.
- Lay infrastructure that the follow-up `refine-onboarding-copy` change can immediately use to migrate `hype.*` → `entity.hype.*` and unify other terminology.

**Non-Goals:**
- Rewrite or migrate any existing i18n keys. Migration is the next change's job.
- Modify protobuf schemas or BSR-published types. No proto changes, no breaking API change, no BSR cycle.
- Generate code from proto into i18n. The lint script verifies parity but does not synthesize keys.
- Define a translation memory or workflow for translators. Out of scope; the JSON files remain the translator's interface.
- Cover backend-emitted user-facing strings (e.g. error messages from RPC). Backend localization is a separate concern.

## Decisions

### Decision 1: Two layers, not one unified glossary

A single `brand-glossary.md` listing every user-facing term would compete with both proto definitions (for entity-grounded terms) and i18n JSON (as the canonical surface label per locale). It would drift from both.

Instead, terms are split by whether they correspond to a protobuf entity:

- **Layer A** (entity-grounded): concept lives in proto, labels live in i18n under a dedicated `entity.*` namespace. No third document.
- **Layer B** (brand expressions): concept and canonical labels live in a single `openspec/specs/brand-vocabulary/spec.md` requirement table. Used for coined phrases that have no entity backing.

**Rule of thumb**: if a term refers to something the backend stores, transmits, or computes, it belongs to Layer A. If it's a marketing phrase, lane name, slogan, or coined product noun, it belongs to Layer B. If a Layer B term ever gets entity-modeled, it migrates to Layer A and is removed from the brand-vocabulary doc.

**Alternative considered**: store labels as protobuf custom options (e.g. `(liverty.ui.v1.label) = { ja: "Stage", en: "Hype" }`). Rejected because it conflates schema concerns with presentation concerns, requires a custom options proto package, and complicates BSR consumers who don't need labels. The i18n JSON is already the right place for surface labels.

### Decision 2: `entity.*` namespace mirrors proto names

The new namespace uses the **lower-camelCase rendering of the protobuf message/enum name** as the second segment, with `label` for the entity name itself and `values.<value>` for enum members:

```jsonc
{
  "entity": {
    "hype": {
      "label": "Stage",                      // JA-side
      "values": {
        "watch":  "Watching",
        "home":   "Home",
        "near":   "Near",
        "away":   "Away"
      }
    },
    "concert":  { "label": "ライブ" },
    "artist":   { "label": "アーティスト" },
    "homeArea": { "label": "ホームエリア" }
  }
}
```

The mirroring is mechanical: `HypeLevel` → `entity.hype` (the `Level` suffix is dropped since the namespace already implies "this is an enum"); `Concert` → `entity.concert`; `User.HomeArea` → `entity.homeArea`. The lint script enforces this mapping.

**Alternative considered**: keep the full enum name (`entity.hypeLevel`). Rejected because in user-facing copy the `Level` suffix reads as redundant Java-isms ("Set your HypeLevel" vs. "Set your Stage"). The UI consumer should see the human-friendly noun.

### Decision 3: Asymmetric labels are explicit and tested

The lint script (a) requires both locales have the same set of `entity.*` keys, (b) does NOT require the values to be translations of each other. JA-only-style keys like `entity.hype.label` ("Stage" in JA, "Hype" in EN) are valid by design and the script is silent about value differences.

This makes the asymmetry of `HypeLevel` explicit: both files must declare a label, but they may pick different surface words. A code reviewer checking the diff sees both at once.

**Alternative considered**: machine-enforce that EN matches the proto field name. Rejected because brand-coined EN labels (like keeping "Hype") would need exemptions, and over time the exemption list would dominate the rule.

### Decision 4: Layer B lives in OpenSpec specs, not in a free-floating markdown

Putting `brand-vocabulary.md` at the repo root or in `docs/` would make it invisible to the OpenSpec workflow. By making it `openspec/specs/brand-vocabulary/spec.md` with proper requirements, it's reviewed and versioned with the same rigor as any other capability, surfaces in `openspec list`, and can declare scenarios (e.g. "WHEN a Layer B term gets entity-modeled, THEN it SHALL be removed from this spec").

**Alternative considered**: a plain markdown file in `docs/`. Rejected because it would not benefit from spec-driven review and would be easy to forget.

### Decision 5: Lint runs in the frontend repo, not specification

The lint script needs to read both `translation.json` files and (optionally) the proto sources. Since the proto sources are remote-generated via BSR for the frontend, the script reads the proto names from a small generated index file (or hardcoded list, for the initial scaffold) rather than parsing `.proto` files directly. The script lives in `frontend/scripts/check-brand-vocabulary.ts` and is invoked from `make lint`.

**Alternative considered**: cross-repo lint in CI. Rejected because the proto repo is the producer and shouldn't depend on consumer i18n state. Frontend CI is the natural place since frontend is the consumer that breaks if labels are missing.

### Decision 6: Initial scaffold ships with zero entity entries

Both `translation.json` files gain an empty `"entity": {}` object. The Layer B spec ships with an initial table of brand expressions known today (HOME STAGE family, "あなただけのタイムテーブル"). The lint script ships and runs but is permissive when `entity.*` is empty (no entries to check).

This keeps the change focused on infrastructure. The `refine-onboarding-copy` follow-up change populates `entity.*` and migrates existing `hype.*` keys.

## Risks / Trade-offs

- **Risk: developers add entity labels without updating brand-vocabulary.md, or vice versa** → Mitigation: the lint script ensures namespace parity in i18n. The Layer B spec is small enough that a code reviewer notices missing entries. We accept that Layer B drift is a doc-discipline problem, not a tooling problem.
- **Risk: the mechanical `HypeLevel` → `entity.hype` mapping breaks for entities like `EventDateGroup` or compound names** → Mitigation: documented in the spec with explicit examples; the lint script either exempts unknown entities or accepts a curated mapping table. Worst case: future entities document an explicit override.
- **Risk: lint script becomes brittle if it parses proto** → Mitigation: the initial implementation reads a hand-curated list of entity names (10–20 entries). A future improvement can derive this from BSR-generated TS types. Avoid coupling to raw `.proto` parsing.
- **Trade-off: introducing a new namespace fragments the i18n file mentally** → Accepted. The `entity.*` namespace is conceptually distinct from page-keyed strings; co-locating them in the same file is convenient but the `entity` top-level marker makes the boundary visually obvious.
- **Trade-off: the follow-up copy change is gated on this** → Accepted. Doing both at once would mix infrastructure with content rewrite, making review harder.
