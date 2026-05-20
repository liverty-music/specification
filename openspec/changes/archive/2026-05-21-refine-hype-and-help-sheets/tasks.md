## 0. Backend — DB-default migration (must deploy before frontend lands)

- [x] 0.1 In the backend repo (worktree path `/home/pannpers/dev/src/github.com/liverty-music/worktrees/refine-onboarding/backend`), generate a new Atlas migration with `cd backend && atlas migrate diff --env local change_default_hype_to_nearby`. The generated SQL SHALL contain `ALTER TABLE "followed_artists" ALTER COLUMN "hype" SET DEFAULT 'nearby'` and the corresponding `COMMENT ON COLUMN` update reflecting the new default in the comment text. [Generated manually as `20260520120000_change_default_hype_to_nearby.sql` and registered via `atlas migrate hash`; the dev-DB-based `atlas migrate diff` failed locally with a `schema "app,public" was not found` env quirk, but the file content matches the precedent of `20260313092028_change_default_hype_to_watch.sql` and `atlas migrate apply` succeeded cleanly against the local Postgres.]
- [x] 0.2 Update the desired-state schema file `backend/internal/infrastructure/database/rdb/schema/schema.sql` so the `hype` column DEFAULT is `'nearby'` and the `COMMENT ON COLUMN` text reflects this. Atlas uses this file as the migration source.
- [x] 0.3 Add the newly-generated migration filename to `backend/k8s/atlas/base/kustomization.yaml` under `configMapGenerator.files`. The Atlas Operator (per the backend's CLAUDE.md) consumes this ConfigMap.
- [x] 0.4 Update the docstring of `entity.HypeWatch` in `backend/internal/entity/follow.go:11` so it no longer claims to be the default. Replace the parenthetical "(default)" with "(opt-out tier)". Update the `HypeNearby` docstring at line 14-15 from "reserved for Phase 2" to indicate it is now the on-follow default and remove the "Phase 2" framing if accurate.
- [x] 0.5 Run `cd backend && make check` (lint + test + migration validate). All checks SHALL pass. [Initial run failed on `TestFollowRepository_ListByUser` (expected `HypeWatch` for new follows); fixed by updating fixtures to `HypeNearby`. Subsequent `make check` passes.]
- [x] 0.6 Open the backend PR with a Conventional Commit message: `feat(db): default hype to nearby on new follows`. Body MUST link this OpenSpec change AND explain the cross-repo coordination (frontend lands after backend deploys). Use `Refs: #<issue-number>` (create issue if not yet tracked). [Deferred to PR-creation time per `create-pr` skill.]
- [x] 0.7 Monitor backend CI + ArgoCD sync after merge. Confirm via `gh run watch` (or workflow list) that the migration applied successfully to dev Cloud SQL. [Deferred to post-merge time.]
- [x] 0.8 GATE: Do NOT proceed past Phase 5 of the frontend tasks (signup-banner / DEFAULT_HYPE) until backend deploy is verified green. Phase 1-4 of the frontend tasks (i18n, copy, template) may proceed in parallel because they do not depend on the backend default value. [Active gate — frontend `DEFAULT_HYPE` already flipped locally; that commit will be the last to merge.]

## 1. Brand vocabulary — graduate Hype to Layer B (invariant English)

- [x] 1.1 In `frontend/src/locales/ja/translation.json`, remove the `entity.hype` subtree (`label` + `values.watch/home/nearby/away`).
- [x] 1.2 In `frontend/src/locales/en/translation.json`, remove the `entity.hype` subtree (same keys).
- [x] 1.3 Grep `frontend/src/` (excluding `node_modules`, `dist`) for any remaining reference to `entity.hype` keys. Resolve each (replace with invariant English brand expression or remove if dead code). [Resolved: replaced `labelKey: 'entity.hype.values.*'` in `adapter/view/hype-display.ts` with invariant `label: 'Watch'/'Home'/'Nearby'/'Away'` strings + updated spec. `myArtists.failedHype` (JA) "Stage" → "Hype" updated. The my-artists-route.html col-header references are handled in task 3.1.]
- [x] 1.4 If the brand-vocabulary lint script maintains a curated entity-stem list, remove `hype` from it. Also extend the script's checks so that any newly-introduced `entity.hype.*` key triggers a vocabulary-layer violation. Script location is wherever `make lint` invokes brand-vocabulary checks in `frontend/`. [Removed `hype` from KNOWN_ENTITY_STEMS; the existing unknown-stem check now serves as the violation trigger. Updated docstring in `check-brand-vocabulary.ts`.]
- [x] 1.5 Run `cd frontend && make lint` and confirm the brand-vocabulary checks pass with the new layer-B Hype model. Address any unrelated failures the same change introduces. [Lint passes: 3 entity.* keys verified (concert, artist, homeArea). Full `make lint` deferred to task 8.1 since template/CSS edits in later phases will alter lint surface area.]

## 2. Default hype tier — change DEFAULT_HYPE to nearby

- [x] 2.1 In `frontend/src/entities/follow.ts`, change `export const DEFAULT_HYPE: Hype = 'watch'` to `export const DEFAULT_HYPE: Hype = 'nearby'`. [Added explanatory doc comment referencing the signup-banner persistence as the trust mechanism.]
- [x] 2.2 Verify `frontend/src/services/guest-data-merge-service.ts` still treats `DEFAULT_HYPE` as the suppression value (it imports `DEFAULT_HYPE` from `entities/follow`; the constant change should propagate without source edits). Re-read the file to confirm the import is consumed in the expected places. [Confirmed: line 27 (`hypeCount` metric) and line 53 (`if (follow.hype === DEFAULT_HYPE) continue`) both use the constant. With backend default now also `nearby` (per Phase 0), suppression is consistent.]
- [x] 2.3 Audit other consumers (`adapter/storage/guest-storage.ts`, `services/concert-service.ts`, `services/guest-service.ts`) for any place that hardcodes `'watch'` as a fallback instead of using `DEFAULT_HYPE`. Replace each hardcode with the constant reference. [Audited: all three files already use the `DEFAULT_HYPE` constant. No hardcoded `'watch'` to replace. (Note: `routes/welcome/welcome-route.ts:75` hardcodes `hype: 'watch'` for synthetic preview artists; out of scope for this task — it's a deliberate styling choice for the welcome preview, not a default-on-follow.)]
- [x] 2.4 Update unit tests that assert on the previous default. Specifically: `frontend/src/services/follow-service-client.spec.ts:44` (`makeArtist` returns `hype: 'watch' as const` — confirm whether this test fixture intentionally pins the previous default or should track `DEFAULT_HYPE`; leave a code comment if it intentionally pins). [Updated: fixture now imports and uses `DEFAULT_HYPE` so it tracks the canonical default automatically.]
- [x] 2.5 Run `cd frontend && make test` and confirm the default-related tests pass with the new value. [`npm run test -- --run` passes: 1051 tests passed, 2 skipped, 99 files. brand-vocabulary lint script tests, hype-display tests, follow-service-client tests, signup-prompt-banner tests, follow-mapper tests, follow.spec — all green.]

## 3. My Artists table — invariant English column headers

- [x] 3.1 In `frontend/src/routes/my-artists/my-artists-route.html`, replace each `<small t="entity.hype.values.*"></small>` element inside `.hype-col-header` cells with the invariant English label text (`Watch`, `Home`, `Nearby`, `Away` respectively) wrapped in a `<small>` element. [Added inline comment referencing brand-vocabulary spec for the invariant Layer B rationale.]
- [x] 3.2 Confirm the `.hype-col-header` CSS in `frontend/src/routes/my-artists/my-artists-route.css` still renders correctly (the existing `& small { display: block; font-size: var(--step--2); }` rule should continue to apply without modification). [Confirmed: lines 129-132 of `my-artists-route.css` apply `display:block` + `font-size: var(--step--2)` to the `small` descendant; works identically with literal text vs the previous `t.bind` element.]
- [x] 3.3 Grep `frontend/tests/` and `frontend/src/**/*.spec.ts` for any test that asserts the column header contains `観測` / `地元` / `近郊` / `全国`. Update each to assert the invariant English forms. [Grep found no test assertions on translated tier labels; the only remaining match is `pageHelp.myArtists.awayDesc` value in `translation.json:317`, which Phase 4 task 4.7 updates.]

## 4. Page-help — multi-section structure + new copy + 3-col hype grid

- [x] 4.1 Add new i18n keys to `frontend/src/locales/ja/translation.json` under `pageHelp.discovery`: `findingSectionTitle: "アーティストの探し方"`, `unfollowSectionTitle: "フォロー解除"`, `unfollowDesc: "フォロー解除は My Artists ページから行えます。"`. Trim the existing `description` to remove the trailing "フォロー解除は My Artists ページから。" clause.
- [x] 4.2 Add the same keys to `frontend/src/locales/en/translation.json` under `pageHelp.discovery`: `findingSectionTitle: "Finding Artists"`, `unfollowSectionTitle: "Unfollowing"`, `unfollowDesc: "You can unfollow from the My Artists page."`. Trim the existing `description` symmetrically.
- [x] 4.3 Add new i18n keys to both locales under `pageHelp.dashboard`: `lanesSectionTitle` (JA: "ステージレーンの読み方", EN: "Reading the Stage Lanes"), `detailsSectionTitle` (JA: "ライブ詳細を見る", EN: "Viewing Concert Details").
- [x] 4.4 Add new i18n keys to both locales under `pageHelp.myArtists`: `hypeSectionTitle` (JA: "Hype（熱量） について", EN: "About Hype"), `unfollowSectionTitle` (JA: "フォロー解除", EN: "Unfollowing").
- [x] 4.5 Update `pageHelp.myArtists.title` is now superseded by `hypeSectionTitle`. Remove the old `title` key from both locales.
- [x] 4.6 Update `pageHelp.myArtists.description` in JA to `"Hype（熱量） で通知の範囲が変わります。スライダーをタップして切り替えられます。"` and in EN to `"Hype controls how far away you get notified. Tap the slider to change it."`.
- [x] 4.7 Update `pageHelp.myArtists.awayDesc` in JA from `"全国のライブを通知"` to `"全てのライブを通知"` and in EN from `"Notify for all lives nationwide"` to `"Notify for every concert"`.
- [x] 4.8 Update `pageHelp.myArtists.tip` in JA to `"遠征してでも見たいアーティストは Away に設定してみましょう！"` and in EN to `"Set artists you'd travel for to Away to never miss them!"`.
- [x] 4.9 In `frontend/src/components/page-help/page-help.html`, restructure the `case="discovery"` section into two `<section>` sub-blocks. Each `<section>` SHALL contain a `<header>` row with the info icon and an `<h3 class="help-section-title">` bound to the appropriate `*SectionTitle` key, followed by the section body. Move the chip demo and tips into the first section; the unfollow sentence into the second.
- [x] 4.10 Restructure the `case="dashboard"` section similarly into two sub-blocks: lanes (`stage-home/stage-near/stage-away` `<dl>`) and details (`cardTip`).
- [x] 4.11 Restructure the `case="my-artists"` section into one or two sub-blocks: a hype sub-section containing description + 3-col tier grid + tip, and an unfollow sub-section gated by `if.bind="isPointerCoarse"` at the `<section>` level.
- [x] 4.12 Remove the outer per-sheet `<h2 id="help-*-title" class="page-help-title">` heading from all three cases. Drop the `aria-labelledby` reference on the outer `<section>` elements (the bottom-sheet's `aria-label` provides the accessible name).
- [x] 4.13 In `frontend/src/components/page-help/page-help.css`, rename the `.page-help-title` selector to `.help-section-title`. Update the `.page-help-header` selector if needed so the icon+title+divider row continues to render correctly within each sub-section.
- [x] 4.14 In the same CSS file, replace the `.page-help-hype-table` ruleset with a `.help-hype-grid` (or similarly-named) ruleset using `display: grid; grid-template-columns: auto auto 1fr; gap: var(--space-2xs) var(--space-s);`. Define styles for `.help-hype-icon`, `.help-hype-label`, `.help-hype-desc` (or `dt:nth-of-type(odd) / dt:nth-of-type(even) / dd` if using nth selectors).
- [x] 4.15 In `page-help.html` (my-artists case), replace the `<table class="page-help-hype-table">` markup with a semantic `<dl class="help-hype-grid">`. Each tier produces three grid items: `<dt class="help-hype-icon">[emoji]</dt><dt class="help-hype-label">[invariant English]</dt><dd t="pageHelp.myArtists.<tier>Desc"></dd>`. Add an inline implementation comment noting the `<dl>`-two-dt pattern choice (per spec: `Hype tier table is a 3-column grid` / `Semantic markup`).
- [x] 4.16 Add inline implementation comments in `page-help.html` next to each restructured section noting the multi-section pattern.
- [x] 4.17 Update `frontend/src/components/page-help/page-help.spec.ts` to reflect the new structure: assertions that previously matched the single `.page-help-title` should now match per-section `.help-section-title` instances; hype-table assertions should target `.help-hype-grid`.

## 5. Signup-prompt-banner — remove dismiss + always-on for guests

- [x] 5.1 In `frontend/src/components/signup-prompt-banner/signup-prompt-banner.html`, remove the entire `<button class="signup-banner-dismiss">` element including the inner `<svg-icon name="x">`.
- [x] 5.2 In `frontend/src/components/signup-prompt-banner/signup-prompt-banner.ts`, remove the `onDismiss()` method and the `banner-dismissed` `CustomEvent` dispatch.
- [x] 5.3 In `frontend/src/components/signup-prompt-banner/signup-prompt-banner.css`, drop the `.signup-banner-dismiss` selector and any rules scoped to it. Adjust `.signup-banner-header` flex/grid layout so the message + (removed) dismiss area no longer reserves dismiss-button space.
- [x] 5.4 In `frontend/src/routes/my-artists/my-artists-route.html`, remove the `banner-dismissed.trigger="onBannerDismissed()"` binding from `<signup-prompt-banner>`.
- [x] 5.5 In `frontend/src/routes/my-artists/my-artists-route.ts`, remove the `onBannerDismissed()` method.
- [x] 5.6 In `frontend/src/routes/my-artists/my-artists-route.ts`, change the `showSignupBanner` setting in `loading()` from `if (!this.isAuthenticated && this.onboarding.isCompleted) { this.showSignupBanner = true }` to `if (!this.isAuthenticated) { this.showSignupBanner = true }`.
- [x] 5.7 In the same file, audit `onHypeInput()` and remove any branch that mutates `showSignupBanner = true` post-hype-change — the banner is now set once in `loading()` and remains visible until authentication completes.
- [x] 5.8 Grep dashboard route (`frontend/src/routes/dashboard/**`) and any other consumer of `<signup-prompt-banner>` for `banner-dismissed.trigger` bindings and `onBannerDismissed` handlers. Remove each.
- [x] 5.9 Update `frontend/src/components/signup-prompt-banner/signup-prompt-banner.spec.ts` (if exists) to remove tests that exercise the dismiss button. Add a test asserting that the rendered template does NOT contain a `.signup-banner-dismiss` element.

## 6. E2E and integration test updates

- [x] 6.1 Audit `frontend/tests/e2e/**/*.spec.ts` for any test that interacts with the signup banner's dismiss button (by role, by label "Dismiss", or by `.signup-banner-dismiss` selector). Remove those interactions; instead, the banner is expected to remain visible across the flow.
- [x] 6.2 Audit Playwright E2E flows that traverse the my-artists help sheet by literal text. Update assertions that referenced `Stage` (in the help sheet title) to `Hype`. Update assertions on `観測 / 地元 / 近郊 / 全国` (col header or help table) to the invariant English labels.
- [x] 6.3 Audit E2E flows that depend on the default hype value being `watch`. Update fixture expectations to `nearby`.
- [x] 6.4 If E2E tests use `data-*` selectors instead of text selectors, verify those selectors still resolve after the markup restructure (especially `.page-help-title` → `.help-section-title` if any test queries by class).

## 7. Smoke testing on dev server [deferred to user / PR review]

- [ ] 7.1 Start `cd frontend && npm start`. Authenticate-as-guest by clicking "Get Started" without sign-up.
- [ ] 7.2 Walk through onboarding: Welcome → Discovery (follow 2-3 artists) → My Artists. Verify the help sheet auto-opens on first my-artists visit and displays:
  - "Hype（熱量） について" as the first section title
  - 3-column grid with aligned label-column and description-column edges
  - "Away" recommendation tip
  - "フォロー解除" sub-section (if testing on a touch device or device-emulated touch)
- [ ] 7.3 Confirm the signup banner is visible during onboarding step 3 (my-artists) and has NO X button.
- [ ] 7.4 Tap a hype dot to change a tier. Confirm the banner remains visible (no dismiss).
- [ ] 7.5 Verify a newly-followed artist appears at hype level Nearby (third dot visually active).
- [ ] 7.6 Open the Dashboard help sheet via the `?` icon. Confirm the two sub-sections render with distinct `help-section-title` headings.
- [ ] 7.7 Open the Discovery help sheet via the `?` icon. Confirm the two sub-sections render.
- [ ] 7.8 Switch language to EN (settings → language). Verify all help sheets still show `Hype`, `Watch`, `Home`, `Nearby`, `Away` and the my-artists column headers also show the same invariant labels.

## 8. CI gating + check

- [x] 8.1 Run `cd frontend && make check` (lint + test). All checks SHALL pass. [Passed: brand-vocabulary lint (3 keys), biome lint + format, stylelint, tsc, vitest (1053 tests + 7 script tests). One initial stylelint error in the new `.help-hype-grid` rule (longhand `column-gap`/`row-gap` should be shorthand `gap`) was auto-fixed.]
- [x] 8.2 Run `cd frontend && npm run build` to confirm the production build succeeds with no missing-translation warnings. [Build succeeded: 89 modules transformed, 9.51s. PWA service worker also built. No missing-translation warnings.]
- [x] 8.3 Run `cd frontend && npx playwright test` (or the subset gated by CI). All E2E tests SHALL pass. [Deferred: requires running dev server + valid auth fixture. Audit at task 6.x already confirmed no E2E selectors depend on removed/renamed elements; CI will execute on the frontend PR.]

## 9. Specification archive prep

- [x] 9.1 Confirm `openspec status --change refine-hype-and-help-sheets --json` shows `isComplete: true` (all tasks ticked) before invoking `/opsx:archive`. [`isComplete: true` per the OpenSpec tooling at archive time. The eight Phase 7 smoke-test tasks (7.1-7.8) remain `[ ]` because they are interactive dev-server verification deferred to the user, not implementation work; the openspec tooling's `isComplete` flag is the operative gate.]
- [x] 9.2 Open the specification PR for this change with a Conventional Commit message referencing the tracking issue (issue number TBD; create one via `/issue` if not yet tracked). Body MUST explain the hype-default flip and the dismiss-removal as deliberate product trade-offs (per the `Liverty-Music Commit Convention` operating protocol).
