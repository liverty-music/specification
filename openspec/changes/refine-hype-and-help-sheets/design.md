## Context

The frontend's My Artists page is the third leg of the onboarding tutorial (Welcome → Discovery → My Artists → Completed). The page-help bottom-sheet that auto-opens on first visit teaches users that the four dots on each artist row represent a graduated notification scope ("Hype tier"). Two cumulative issues have made that tutorial moment weaker than it should be:

1. **Lexical mismatch.** The JA help sheet titles the concept "Stage" (because `entity.hype.label` in JA was set to `"Stage"` per an existing brand-vocabulary scenario allowing asymmetric locale labels), but no other surface in the app uses the word "Stage" for this concept — the Dashboard timetable uses "STAGE" for *lanes* (a different concept), and the my-artists table column headers translate the tier names to ja-only forms (`観測 / 地元 / 近郊 / 全国`). A user reading the help sheet sees one word, then turns to the page and sees another. The help sheet's hype-table header also packs `[emoji][space][label]` into one `<th>` cell, so the label-column edges never line up vertically.

2. **Notification opt-in friction.** The default hype value for a new follow is `watch` ("dashboard view only, no push notifications"). Guests can complete onboarding having followed five artists yet never see what the notification system is for, because nothing about their `watch`-default follows produces a notification commitment. Combined with the dismissable signup banner, the entire notification model is opt-in via discovery — users who don't change a single hype dot during onboarding leave thinking the app is "just a dashboard."

This change bundles both fixes — a copy/structure refinement of the help sheet AND a default-tier flip AND a non-dismissable signup banner — under one OpenSpec change because they share a single design hypothesis: the my-artists tutorial moment should communicate that **following an artist is, by default, a notification commitment** (Nearby), and that **commitment is only honored after sign-up** (banner persistence). Each piece in isolation would only be partial.

A related, narrower change `refine-onboarding-copy` is currently in flight (33/38 tasks complete) but explicitly scoped to onboarding copy only — it did not touch hype defaults, help-sheet structure, or banner behavior. This new change builds on that one but does not depend on it being archived first; the two have no overlapping files.

## Goals / Non-Goals

**Goals:**

- Eliminate the word "Stage" as a JA alias for the Hype concept anywhere outside the timetable's lane labels. The hype tier surface labels (`Watch / Home / Nearby / Away`) become invariant English brand expressions, consistent across all surfaces.
- Restructure all three onboarding help sheets (Discovery, Dashboard, My Artists) into a multi-section pattern with a single reusable `.help-section-title` class, dropping the per-sheet single `.page-help-title`. The same pattern accommodates 1 or more sections per sheet.
- Render the my-artists hype tier explanation as a 3-column grid (icon / label / description) where the label-column and description-column edges are vertically aligned across all four tier rows.
- Change `DEFAULT_HYPE` from `watch` to `nearby` so that following an artist is, by default, a notification opt-in within ≈200 km of the user's home area.
- Remove the dismiss `X` button from the signup-prompt-banner entirely; persist the banner across the entire guest-on-my-artists lifecycle, including during onboarding step 3.

**Non-Goals:**

- Renaming the Dashboard timetable's lane labels (`HOME STAGE / NEAR STAGE / AWAY STAGE`). "Stage" in that context means "lane" — a separate concept from "Hype tier" — and the labels stay as the existing Layer B brand expressions. The proto enum (`HypeType`) is also unchanged; this is purely a UI/copy/default change.
- Rewriting the post-signup notification-permission flow. The current `post-signup-dialog` capability already handles browser push permission acquisition. We rely on it unchanged: a guest who has Nearby-defaulted follows, completes signup, sees the existing notification-enable prompt, and grants permission.
- Migrating existing followed-artist records. Stored `watch` values stay as `watch`; only newly-created follows pick up the new default. The backend DB-default change is forward-looking only — no `UPDATE` against existing rows.
- Adding a "Near" label variant. The convention is `Nearby` everywhere a per-artist Hype tier is shown; `NEAR STAGE` (timetable lane) stays as-is.
- Adjusting the Dashboard's during-onboarding banner visibility. The spec already excludes the banner from Dashboard during onboarding (`onboarding-tutorial` popovers occupy that attention), and this change does not modify that.

## Decisions

### Decision 1: Hype tier surface labels graduate from Layer A (entity) to Layer B (brand)

**Choice.** Remove `entity.hype.label` and `entity.hype.values.*` from the `entity.*` i18n namespace. Add `Hype`, `Watch`, `Home`, `Nearby`, `Away` to the brand-vocabulary registry as Layer B invariant brand expressions.

**Alternatives considered.**

- *(a) Keep in Layer A, change JA labels to match EN (`観測` → `Watch`, etc.).* This would technically deliver the same on-screen text, but it leaves the `entity.hype.*` keys in place — meaning the locale-parity lint still applies, and the brand-vocabulary spec's "asymmetric locale labels" scenario for `HypeLevel` (which currently *permits* `Stage` in JA) stays valid but unused. Future contributors might re-introduce divergent JA labels.
- *(b) Layer B with bilingual entries (e.g., JA: "Hype（熱量）", EN: "Hype").* Mixing the parenthetical gloss into the canonical label conflates the brand expression with prose. The gloss belongs in the help-sheet description sentence, not in the label everywhere it appears.

**Rationale for chosen path.** Layer B with invariant English is the cleanest: it codifies that the four hype tier names are brand vocabulary (like `HOME STAGE / NEAR STAGE / AWAY STAGE` already is), and the locale-parity lint becomes irrelevant for these tokens. The Japanese gloss `(熱量)` appears exactly once — in the help-sheet description sentence — where it functions as a teaching moment rather than a label.

### Decision 2: Default hype = `nearby`, with the signup-banner persistence as the trust mechanism

**Choice.** `DEFAULT_HYPE: Hype = 'nearby'`. Combined with a persistent (non-dismissable) signup banner on My Artists for all guest users.

**Alternatives considered.**

- *(a) Default = `home`.* Less aggressive — only home-area concerts trigger notifications. But "home-area" is a single ISO 3166-2 subdivision, often quite small. For a fan in a low-event subdivision (most of Japan outside Tokyo/Osaka/Aichi), this would yield zero notifications and re-create the original "the app is just a dashboard" problem at a lower volume.
- *(b) Default = `watch` (status quo) with stronger help-sheet nudging toward Nearby/Away.* This relies on users following the help sheet's prescription. Preview-testing telemetry showed that most users dismiss the help sheet without making a single hype change, so prescriptive copy alone does not move the metric.
- *(c) Default = `nearby` with the banner remaining dismissable.* This was the original product instinct, until we recognized that a dismissable banner produces the failure mode: guest dismisses banner, follows continue to be Nearby-defaulted, but no signup happens, and no notifications are ever delivered — the user is left with a silent commitment.

**Rationale for chosen path.** The Nearby default makes the notification commitment legible immediately; the non-dismissable banner ensures the commitment cannot be silently abandoned. The pair is honest: we promise notifications by default, and we keep saying "you need to sign up to actually get them" until the user either signs up or stops being a guest. Removing the dismiss button is *less* product-complexity, not more — the alternative (a `dismissable` bindable with two visibility modes) was rejected on KISS grounds (per user direction).

### Decision 3: One `<h3 class="help-section-title">` per help sub-section; no sheet-level `<h2>`

**Choice.** Each help sheet is composed of one or more `<section>` blocks. Each section's title is an `<h3 class="help-section-title">` rendered with the same visual treatment (icon + heading + bottom border) that `.page-help-header + .page-help-title` formerly produced. The bottom-sheet itself carries the accessible name via its existing `aria-label`.

**Alternatives considered.**

- *(a) Two-level heading hierarchy: sheet-level `<h2>` ("My Artists ヘルプ") + section-level `<h3>`.* Visually redundant — the sheet is already opened from the page where the title bar says "My Artists". The h2 would just repeat that.
- *(b) Implicit sections (no `<h3>`, just visual spacing).* Cheaper visually but worse for accessibility and content scannability. The user explicitly wants the structure to feel like discrete sections.

**Rationale for chosen path.** A single heading level per visible section keeps the hierarchy flat and readable. The bottom-sheet itself is a landmark (it's an `aria-label`'d dialog), so the section `<h3>`s sit one level below the implicit "Page help" landmark — semantically clean.

### Decision 4: 3-column hype table → CSS Grid `auto auto 1fr`, semantic `<dl>` markup

**Choice.** Replace the existing `<table class="page-help-hype-table">` (2-col) with a `<dl class="help-hype-grid">` that uses `grid-template-columns: auto auto 1fr` with `gap: var(--space-2xs) var(--space-s)`. Each tier produces three grid items: a `<dt class="help-hype-icon">` (icon), a `<dt class="help-hype-label">` (invariant English label), and a `<dd class="help-hype-desc">` (notification scope sentence).

**Alternatives considered.**

- *(a) Keep `<table>` markup, use 3 `<td>` per row.* Works visually with `table-layout: auto`, but `<table>` carries header-relationship semantics (`scope="row"` on the icon cell) that don't naturally model "icon + label = one composite label, description = the definition." A definition list with two `<dt>`s per `<dd>` is a known accessibility pattern for this kind of "key-key-value" mapping.
- *(b) CSS Grid on a flat sequence of `<div>`s.* Loses semantic markup entirely. We have an actual semantic concept (term → definition), so we should encode it.
- *(c) `display: contents` on a row wrapper.* Browser-buggy on some platforms (notably Safari historically dropped accessibility role); not worth the risk for this small benefit.

**Rationale for chosen path.** `<dl>` with the icon and label as two `<dt>` elements within a single term-group preceding a single `<dd>` is the correct semantic structure ("the term 'Watch' (👀) has the definition '通知なし'"). CSS Grid lets the auto-width columns track the widest icon and widest label naturally, eliminating the ragged-edge complaint.

### Decision 5: Signup banner — strip dismiss entirely, drop the bindable plan

**Choice.** Delete the `<button class="signup-banner-dismiss">` markup, the `onDismiss()` method, the `banner-dismissed` custom event, all host bindings (`banner-dismissed.trigger=…`), and all host handlers (`onBannerDismissed()`). No `dismissable` bindable is introduced.

**Alternatives considered.**

- *(a) Add a `dismissable` bindable (default true) and let hosts pass `dismissable.bind="!isOnboarding"` to control X visibility.* Initially proposed in exploration. Rejected because: (i) it preserves a UI complexity (the X button) we don't actually want post-onboarding either — the signup banner serves a single, persistent purpose for any guest; (ii) every host page would need a new binding; (iii) the user's direction was explicit: "ロジックを複雑にしてまで guest 利用を推奨する必要は無いので、ボタンは削除して."

**Rationale for chosen path.** The simplest version: the banner is shown when the host decides it should be shown, and the user cannot dismiss it. The host's `visible.bind` is the only visibility control.

### Decision 6: My Artists banner visibility — guest-on-my-artists is sufficient

**Choice.** `showSignupBanner = !isAuthenticated` on the My Artists page, set once on `loading()`, with no further mutation in `onHypeInput()`.

**Alternatives considered.**

- *(a) Keep the existing logic: set on `loading()` only if `onboarding.isCompleted`, then also set in `onHypeInput()` when a hype change occurs during onboarding.* This was the source of the original problem — without a hype change, the onboarding-step guest never sees the banner.
- *(b) Set in `loading()` unconditionally for guests, even during onboarding.* Chosen. The onboarding popover guidance doesn't conflict with a fixed-bottom banner — they occupy different screen zones. And it's the only path that surfaces the banner the moment a guest arrives at my-artists during onboarding-step 3.

**Rationale for chosen path.** Guest + my-artists is a stable, unambiguous condition. There is no scenario where we want to suppress the banner in that combination.

### Decision 7: Help sheet sub-sections — concrete copy decisions

Sub-section titles (new i18n keys):

| Key | JA | EN |
|---|---|---|
| `pageHelp.discovery.findingSectionTitle` | アーティストの探し方 | Finding Artists |
| `pageHelp.discovery.unfollowSectionTitle` | フォロー解除 | Unfollowing |
| `pageHelp.dashboard.lanesSectionTitle` | ステージレーンの読み方 | Reading the Stage Lanes |
| `pageHelp.dashboard.detailsSectionTitle` | ライブ詳細を見る | Viewing Concert Details |
| `pageHelp.myArtists.hypeSectionTitle` | Hype（熱量） について | About Hype |
| `pageHelp.myArtists.unfollowSectionTitle` | フォロー解除 | Unfollowing |

The Discovery `unfollow` sub-section (current one-liner inside the `description`) becomes:

- JA: `フォロー解除は My Artists ページから行えます。`
- EN: `You can unfollow from the My Artists page.`

Keyed as `pageHelp.discovery.unfollowDesc`. The existing `pageHelp.discovery.description` SHALL be trimmed to remove the unfollow sentence.

Dashboard `details` sub-section uses the existing `pageHelp.dashboard.cardTip` key — no new copy beyond the section title.

My-Artists `unfollow` sub-section uses the existing `pageHelp.myArtists.longPressTip` key — no new copy beyond the section title. The `if.bind="isPointerCoarse"` gate is moved up to the `<section>` element so the entire sub-section (heading + tip) is conditionally rendered.

## Risks / Trade-offs

- **Risk:** Aggressive default (`nearby`) generates user surprise — "I followed one artist and suddenly the app says I'll be notified for everything within 200 km?"
  **Mitigation:** The help sheet auto-opens on first my-artists visit during onboarding, explains the four tiers, and shows that Nearby is the second-strongest tier — not the most aggressive. The signup banner reinforces that nothing actually fires until signup.

- **Risk:** Non-dismissable banner feels like nagging UX. Users with no intent to sign up have no escape valve.
  **Mitigation:** Banner is fixed-bottom (~70px) and uses frosted glass — it doesn't block the artist list. Guest mode is itself opt-in (the user chose to skip signup at Welcome). Trade-off acknowledged: this is a deliberate increase in signup-prompt pressure.

- **Risk:** Removing `entity.hype.values.*` from JA breaks any tests that asserted on the translated forms (`観測 / 地元 / 近郊 / 全国`).
  **Mitigation:** Task list explicitly includes an audit pass for these strings. The brand-vocabulary lint will catch any orphaned `entity.hype.*` reference once the keys are removed.

- **Risk:** The multi-section help-sheet restructure is a larger CSS refactor than it looks. The `.page-help-title` and `.page-help-header` rules are entangled with each section's content. A regression on Discovery or Dashboard help layouts is possible.
  **Mitigation:** Existing Storybook stories for `page-help` (if any) and the Playwright E2E flow for onboarding need to be exercised for all three sheets, not just my-artists.

- **Risk:** Dismiss button removal silently breaks any documented test or Playwright assertion that expected the button to be present (`getByLabel('Dismiss')` etc.).
  **Mitigation:** Grep the test suite for the dismiss selector during implementation; the tasks list calls this out as a discrete audit step.

- **Risk:** The backend DB-default migration and the frontend `DEFAULT_HYPE` change can fall out of sync if either PR merges without the other deploying. A user could see the my-artists table render Nearby dots while their actual backend records are still `watch` (frontend merged but backend not yet deployed), OR backend deploys first and the frontend still says `watch` as the default (backend ready but frontend not yet merged).
  **Mitigation:** Per the Migration Plan, the gate is "backend migration applied to dev" before merging the frontend PR. The temporary state (backend deployed, frontend not) is benign — fresh follows get `nearby` on the backend, the frontend doesn't yet display its own default narrative, but `ListFollowed` will return `nearby` for new follows which is the intended end state. The dangerous order (frontend merged first) is what the gate prevents.

- **Risk:** The `refine-onboarding-copy` change in flight (33/38 tasks) is *also* about onboarding text and could conflict with this change if archived at the same time. Specifically, both changes might touch `frontend/src/locales/ja/translation.json` and `pageHelp.myArtists.*` keys.
  **Mitigation:** This change explicitly does NOT touch the keys that `refine-onboarding-copy` modifies (it leaves all `welcome.*`, `discovery.popoverGuide`, `userHome.*`, `eventDetail.*` keys alone). The `pageHelp.myArtists.*` subtree is touched by this change only — `refine-onboarding-copy` left it untouched. Sequencing: archive `refine-onboarding-copy` first if it lands first; if not, the merge conflict surface is well-bounded.

## Migration Plan

This change spans two repos (backend + frontend) and one DB schema change. Sequencing matters: the frontend's stated default (`nearby`) only matches reality if the backend column default has shipped first.

**Cross-repo order:**

1. **Backend PR** (this OpenSpec change): add Atlas migration `ALTER TABLE "followed_artists" ALTER COLUMN "hype" SET DEFAULT 'nearby'` + matching `COMMENT ON COLUMN` update. Add the new file to `k8s/atlas/base/kustomization.yaml` `configMapGenerator.files`. CI verifies `make check` (lint + test, including migration-rebase guard).
2. **Merge backend PR** → ArgoCD's `backend-migrations` Application syncs the new ConfigMap → Atlas Operator runs the migration against dev Cloud SQL → DB column default is now `nearby`.
3. **Verify backend deploy** via `gh run watch` on the backend repo's ArgoCD-related workflow, OR by querying the migration's effect (any tooling that lists active column defaults). Until this is verified green, the frontend PR SHOULD NOT merge.
4. **Frontend PR** (this OpenSpec change): all the i18n, template/CSS, signup-banner, and `DEFAULT_HYPE` changes. Frontend CI does not depend on backend state (it uses mocked RPCs), so the PR can be opened in parallel and reviewed alongside the backend PR. The merge gate is "backend migration applied to dev".

**Within-repo commit sequencing (each repo):**

Backend repo:
- Single commit: migration file + kustomization update + (optional) docstring tweak on `entity.HypeWatch` describing that it is no longer the default.

Frontend repo (in order):
1. Land i18n key changes (additions + removals) + brand-vocabulary lint-script tweak (removing `hype` from KNOWN_ENTITY_STEMS). Pure data; no template consumption yet.
2. Land the page-help template/CSS restructure and the my-artists template change. Coupled (neither can render without the new keys); ship together.
3. Land the `DEFAULT_HYPE` constant change and the signup-banner persistence change. These touch product behavior and the release notes should call them out.

**Spec change archive** lands in the specification repo separately (via `/opsx:archive`) after both backend and frontend PRs merge and dev is verified.

**Rollback strategy.** Each commit is independently revertable. The DB-default migration is a SET DEFAULT statement with no data writes — rolling it back is a one-line counter-migration (`SET DEFAULT 'watch'`) with no impact on existing rows. The frontend's `DEFAULT_HYPE` constant rollback is a one-line edit. If something goes wrong post-deploy, the safest order is: revert frontend first (so the UI stops advertising `nearby`), then revert backend (so the DB default re-aligns).

## Open Questions

- **Lint script: keep `entity.hype` namespace as an empty placeholder or remove entirely?** Current direction is to remove it entirely, but the brand-vocabulary lint script needs to be checked: if it iterates known entity stems from a curated list, the `hype` stem must be removed from that list at the same time, otherwise the script will warn on missing keys.

- **Should the my-artists `loading()` set `showSignupBanner` synchronously before the artist list resolves, or after?** Today's code sets it inside the `finally` block. Setting it before would cause the banner to flash in during the loading state for a sub-second. Recommendation (not yet decided): keep the post-resolve placement so the banner appears together with the artist list, but the spec scenario should describe the post-resolve guarantee, not the pre-resolve timing.
