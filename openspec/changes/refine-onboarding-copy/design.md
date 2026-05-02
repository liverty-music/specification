## Context

The user-facing copy across Liverty Music's onboarding flow was audited end-to-end during exploration. The audit surfaced three categories of problem:

1. **Terminology drift** — same concept, different words (`ライブ`/`コンサート`, `ダッシュボード`/`タイムテーブル`/`ライブカレンダー`, `登録`/`フォロー`, "Hype" used directly in JA UI).
2. **Cold-start ambiguity** — first-time visitors can't tell what the product is from the welcome hero alone.
3. **Stale labels** — `Music DNA` orb name, `チュートリアルお疲れさま` retroactive framing, always-visible Hype guide row in PostSignupDialog don't fit current product voice.

The previously-shipped `establish-brand-vocabulary` change provides the infrastructure (`entity.*` i18n namespace, parity lint, curated entity list, Layer B brand-expressions registry). This change consumes that infrastructure to deliver the actual content fixes.

Two design choices shape the entire change:

- **Asymmetric localization is intentional**: `HypeLevel` enum keeps its proto name; the JA locale renders it as `Stage` (consuming the existing `HOME STAGE / NEAR STAGE / AWAY STAGE` brand vocabulary), the EN locale stays `Hype` (an established loanword in Western fan culture). No proto change, no BSR cycle.
- **Copy-only, no behavior change**: dashboards, RPCs, auth, routing all unchanged. Even the modal placements (Home Area Selector after dashboard arrival; PostSignupDialog after auth) are deliberately preserved.

## Goals / Non-Goals

**Goals:**
- Move all `HypeLevel`-related labels into `entity.hype.*` so the new namespace is exercised end-to-end and the parity lint has real data to verify.
- Unify `ライブ` / `タイムテーブル` / `フォロー` as the single canonical JA term for each concept across the app (eliminate `コンサート`, `ダッシュボード` (in user copy), `ライブカレンダー`, `登録`).
- Refresh the welcome hero to disambiguate the product, refresh the signup gate to lead with value not method, and refresh the post-signup dialog to celebrate the moment instead of presenting a checklist.
- Drop the `Music DNA` orb label entirely; let the screen function speak for itself without a coined name that exists in neither the entity layer nor any other surface vocabulary.

**Non-Goals:**
- **No proto changes**. `HypeLevel` enum, `Concert`, `Artist`, `User.HomeArea` all keep their protobuf names. This is purely a presentation refresh.
- **No flow restructuring**. Home Area Selector stays as a modal after dashboard arrival; the sequence welcome → discovery → dashboard preview → signup is preserved.
- **No new components or routes**. Only existing components/templates have their copy and (where keys are renamed) their i18n bindings updated.
- **No progress indicator**. Discussed and rejected — the existing 3-screen flow is short and self-explanatory; an indicator would add visual debt without paying for itself.
- **No fallback preview** for the welcome screen. When `dateGroups` is empty the user falls back to the inline CTAs that already exist; building a static demo for the rare case where preview-artist data is unavailable adds engineering surface for marginal benefit.
- **No backend localization**. Backend-emitted user-facing strings (RPC error messages) remain English in this change.

## Decisions

### Decision 1: Migrate `hype.*` keys to `entity.hype.*`, do NOT keep dual paths

The existing `hype.watch / home / nearby / away` keys (and the screen-local references in `myArtists.table`, `myArtists.hypeExplanation`, `postSignup.hypeGuideLabel`, etc.) are replaced by single canonical paths under `entity.hype.values.*` and `entity.hype.label`. Components that previously bound to scattered keys all switch to the canonical path.

**Alternative considered**: keep `hype.*` as legacy aliases, gradually migrate consumers. Rejected because:
- The number of consumers is small (single-digit components).
- Dual paths defeat the parity lint (which entry is authoritative?).
- The `establish-brand-vocabulary` lint will *fail* if `entity.hype.*` exists in only one locale, so half-migration is impossible.

### Decision 2: Keep "Music DNA Orb" as the internal component name, drop only the user-facing label

The `dna-orb` component name and the spec-level `artist-discovery-dna-orb-ui` capability description ("Music DNA Orb glass sphere") are preserved — they are internal nomenclature shared by code and architecture documents. Only the i18n key `discovery.orbLabel: "Music DNA"` (and any user-visible heading derived from it) is removed.

**Alternative considered**: rename component, capability, and label all together. Rejected because the internal name has no user impact and renaming carries a high refactor cost (architecture docs, screenshots, code review history) for zero user-visible benefit.

### Decision 3: PostSignupDialog Hype guide is removed, not relocated as a copy edit

The "Hype guide hint always visible" requirement in the post-signup-dialog capability is REMOVED, not modified. The dialog becomes celebration-first; notification + PWA become optional power-up rows. The Hype guide concept is left to the My Artists page itself; first-time discoverability is an accepted regression (the previously-existing `myArtists.coachMark.setHype` i18n key was never rendered by any component and was deleted in this change — see the Discoverability trade-off note in the post-signup-dialog spec). If the team later judges this regression to be meaningful, a follow-up change can wire an in-page hint or coach mark.

This is a spec-level removal (REMOVED Requirement) because the existing scenarios assert the row is *always* visible regardless of permission state — that invariant no longer holds.

**Alternative considered**: keep the row but rephrase. Rejected because the row competes with the celebration moment and serves a context (the My Artists page) the user hasn't navigated to yet — the guidance is misplaced more than miswritten.

### Decision 4: Empty/error microcopy gets one tone split, not full taxonomy

The boilerplate `失敗しました。もう一度お試しください` appears in 6+ keys. We split it into exactly two tones:
- **Network / connectivity tone**: "ネットワークが不安定なようです。少し時間を置いてもう一度お試しください。"
- **Transient / generic tone**: keep close to the existing "失敗しました。もう一度お試しください。"

**Alternative considered**: classify by error category (auth / data / permission / etc.) with five tones. Rejected — this is copy refinement, not an error-handling overhaul. A two-tone split is the smallest improvement that addresses the "too cold, too uniform" critique without requiring per-error-category routing changes.

### Decision 5: Brand expressions in Layer B are extended only if a phrase recurs

We do NOT preemptively register every coined phrase from the rewrites in `brand-vocabulary.md` Layer B registry. A phrase becomes a Layer B entry only if:
- it appears in 2+ user-visible places, OR
- it is a noun the team will say in conversation (lane name, slogan).

Most rewritten copy is one-shot screen text and does not need cataloguing. The HOME/NEAR/AWAY STAGE family stays as the canonical Layer B entries (already there from `establish-brand-vocabulary`).

### Decision 6: Page-by-page copy is finalized in code review, not pre-locked in spec scenarios

Spec scenarios assert *invariants* (e.g. "PostSignupDialog leads with a celebration row") rather than *exact strings* (e.g. "the title is `🎉 準備完了！…`"). This keeps the spec stable across small wording iterations and avoids the spec/code drift trap where every wording tweak requires a spec edit.

The final wording for each screen is agreed in the implementation PR, not in this change folder. Tasks list the screens to address but the proposed text in tasks.md is illustrative.

## Risks / Trade-offs

- **Risk: a JA-only term replacement (e.g. `登録` → `フォロー`) hits a string in a context I missed (an aria-label, a snack-bar message, a story file)** → Mitigation: grep for every old term in `frontend/src/**/*.{ts,html}` and `frontend/src/locales/`; reviewer checks the diff against the unification table in tasks.md.
- **Risk: removing `discovery.orbLabel` breaks an aria-label that screen readers depend on** → Mitigation: confirm the orb container has either a different aria-label or a `<h1>`/`<h2>` heading announcing the screen purpose; if not, add one before deleting `orbLabel`.
- **Risk: PostSignupDialog tests in `frontend/test/components/post-signup-dialog.spec.ts` assert the always-visible Hype row** → Mitigation: those assertions get inverted ("Hype row SHALL NOT be present"). Existing tests for notification / PWA rows continue to pass since their requirements don't change.
- **Risk: the lint script catches a parity violation immediately when we populate `entity.hype.*` because of a typo** → Mitigation: this is the lint working as intended; fix the typo and move on.
- **Trade-off: spec scenarios stay loose (invariants, not strings)** → Accepted. Tighter scenarios would catch wording regressions but at high churn cost.
- **Trade-off: documentation snapshots (capability descriptions, architecture docs) that reference `Music DNA Orb` are not revisited** → Accepted. The internal name is fine; only user-visible removal happens.

## Migration Plan

1. Land the `entity.hype.*` JSON additions to both locales in a single commit (lint must pass after this commit).
2. Update each consumer to bind to `entity.hype.*` and remove the corresponding old `hype.*` / inline keys in the same commit (so lint sees no orphans).
3. Welcome / signup / discovery / post-signup copy edits as their own commits, one screen per commit, so reviewers can react per screen.
4. Empty/error tone split as a final commit.

Rollback is a straightforward revert at any commit boundary; no schema migration, no data migration, no caches to invalidate.

## Open Questions

- **Final wording for the welcome hero descriptor line.** Three options on the table from exploration: 「推しのライブを集めて、あなただけのタイムテーブルに」, 「ライブ通知 × あなただけのタイムテーブル」, or omit and tighten the existing subtitle. Decided in the implementation PR, not here.
- **Whether to also unify `ライブ` in the i18n key for `notification.title` ("ライブイベントを見逃さない") to match the rest of the copy ("ライブ" not "ライブイベント")**. Probably yes, but worth a moment in review.
- **EN-side wording for `entity.hype.values.*`**. Current proposal: `Watching / Home / Near / Away`. Open whether `Anywhere` reads better than `Away` for the highest level.
