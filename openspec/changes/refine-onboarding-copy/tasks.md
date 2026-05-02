## 1. Setup

- [x] 1.1 Create branches in `specification/` and `frontend/` (issue numbers to be assigned) — specification#433 → branch `433-refine-onboarding-copy`; frontend#348 → branch `348-refine-onboarding-copy`
- [x] 1.2 Confirm `establish-brand-vocabulary` is fully merged on `frontend/main` (`entity.*` namespace + lint script in place) — confirmed via `make lint` baseline output: `brand-vocabulary lint OK (0 entity.* keys verified across JA + EN)`
- [x] 1.3 Run `make lint` baseline on a clean branch checkout to confirm green start

## 2. Layer A Population: Hype → Stage / Hype

- [x] 2.1 In `frontend/src/locales/ja/translation.json` add under the `entity` namespace
- [x] 2.2 In `frontend/src/locales/en/translation.json` add under the `entity` namespace (parity required by lint)
- [x] 2.3 Run `npx tsx scripts/check-brand-vocabulary.ts` and confirm passes — confirmed: "8 entity.* keys verified across JA + EN" (5 from hype + 3 from other entity labels)
- [x] 2.4 Decide final wording on the EN side for `away` — picked **Away** (parallel to existing `HOME / NEAR / AWAY STAGE` lane vocabulary)

## 3. Layer A Population: Other Entities

- [x] 3.1 Add `entity.concert.label`: JA `"ライブ"` / EN `"Live"`
- [x] 3.2 Add `entity.artist.label`: JA `"アーティスト"` / EN `"Artist"`
- [x] 3.3 Add `entity.homeArea.label`: JA `"ホームエリア"` / EN `"Home Area"`
- [x] 3.4 Re-run lint, confirm parity — done with 2.3

## 4. Migrate Existing Hype Bindings to `entity.hype.*`

- [x] 4.1 Replace `t="hype.watch"` / `hype.home` / `hype.nearby` / `hype.away` bindings throughout templates with `t="entity.hype.values.{watch,home,nearby,away}"` — note: TS `Hype` enum value is `nearby` (5 chars), not `near`; entity namespace mirrors it
- [x] 4.2 Replace any `i18n.tr('hype.<x>')` calls in TS with the new path — `HYPE_TIERS` in `src/adapter/view/hype-display.ts` updated
- [x] 4.3 ~~Update `myArtists.coachMark.setHype` text~~ — **skipped per option B**: the i18n key is not rendered by any component (dead key), so it was deleted instead of updated. See post-signup-dialog spec delta for the discoverability trade-off note.
- [x] 4.4 Update `pageHelp.myArtists.title` JA from `"Hypeレベルについて"` to `"Stage について"` and `pageHelp.myArtists.description` JA from `"Hypeレベルで通知の範囲が変わります…"` to `"Stage で通知の範囲が変わります…"` — note: the originally-listed `myArtists.hypeExplanation.title` was a dead key tree (no component rendered it) and has been deleted instead
- [x] 4.5 Reconcile `myArtists.table.{watch,home,nearby,away}` and `myArtists.hypeExplanation.*` against the canonical `entity.hype.values.*` — `myArtists.table.{watch,home,nearby,away}` deleted (replaced by `entity.hype.values.*` bindings in `my-artists-route.html`); `myArtists.hypeExplanation.*` was dead and deleted
- [x] 4.6 Delete legacy `hype.*` top-level keys from both locales — done; also deleted dead `myArtists.coachMark` and `myArtists.spotlight` namespaces in the same sweep
- [x] 4.7 Run `npx tsc --noEmit` to confirm no orphaned key references; run `make lint` end-to-end — both pass

## 5. Terminology Unification

- [x] 5.1 In JA i18n: replace remaining `コンサート` occurrences with `ライブ` — `notification.description` and `notification.blocked.description` updated; also normalized `ライブイベント` → `ライブ` in `dashboard.error.load` and `notification.title`
- [x] 5.2 In JA i18n: replace user-facing `ダッシュボード` occurrences with `タイムテーブル` — only hit was `discovery.generateDashboard`; `dashboard.coachMark.viewArtists` already says `アーティスト一覧` (no ダッシュボード)
- [x] 5.3 In JA i18n: replace user-facing `ライブカレンダー` occurrences with `タイムテーブル` — no occurrences found in JA file (sweep clean)
- [x] 5.4 In JA i18n: replace `登録` (in the sense of "follow") with `フォロー` — `welcome.hero.subtitle` updated; `postSignup.title` / `postSignup.ariaLabel` use 登録 in the account-registration sense (correct usage, untouched)
- [x] 5.5 EN parity check — `entity.concert.label` EN changed from `"Live"` to `"Concert"` (more natural EN noun); existing EN copy keeps "concert" / "live show" as written. The asymmetric-labels pattern: JA `entity.concert.label = "ライブ"`, EN `entity.concert.label = "Concert"`

## 6. Discovery: Drop "Music DNA"

- [x] 6.1 Remove `discovery.orbLabel` from both locales
- [x] 6.2 Update the `dna-orb` template / component to drop the user-facing label — already not bound by any template/TS file (the i18n key was orphaned), so no template change required
- [x] 6.3 Update `discovery.popoverGuide` JA to a reward-predicting phrasing — JA: `"気になるアーティストをタップ — 選んだ推しのライブが、次のステップでタイムテーブルになります"`; EN: `"Tap the artists you care about — your picks become a timetable in the next step"`
- [x] 6.4 Update `discovery.coachMark.viewTimetable` JA — already correct
- [x] 6.5 Update `discovery.generateDashboard` to `"👉 タイムテーブルを生成する"` / `"👉 Generate Timetable"`

## 7. Welcome Hero Refresh

- [x] 7.1 Add a one-line product descriptor under the brand name — picked **`推しのライブを集めて、あなただけのタイムテーブルに`** (JA) / **`Follow your favorite artists. Build your personal timetable.`** (EN). Wired via new i18n key `welcome.hero.descriptor` and rendered in `welcome-route.html` between brand and title; CSS class `welcome-descriptor` added
- [x] 7.2 Restructure CTA labels — `welcome.cta.getStarted` JA: `"使ってみる"` → `"推しを選んでみる"` / EN: `"Get Started"` → `"Pick your artists"` (predicts the next screen); login CTA unchanged
- [x] 7.3 Promote `welcome.guestFriendly` — JA: `"アカウント不要でお試しいただけます"` → `"アカウント不要・30秒で体験"` / EN updated similarly. Sub-line placement above CTA group on Screen 2 (already there); also added the same line to the Screen 1 fallback CTA path (was previously absent there) so the no-account-required message is visible whether or not preview data loads

## 8. Signup Gate Refresh

- [x] 8.1 Delete `チュートリアルお疲れさまでした！` from `signup.description`
- [x] 8.2 Restructure `signup.title` and `signup.description` as value-first — JA title `"あと一歩で、推しのライブを逃さなくなる"`, body 3-bullet list (🔔 通知 / 📱 端末横断 / 🎟 チケット保存); EN title `"One step away from never missing a show"` with parallel bullets. Note: in-app templates do not currently render these keys (no `t="signup.*"` consumers found); the keys are presumed used by Zitadel external auth templates. If they are dead, this rewrite still benefits any future in-app rendering
- [x] 8.3 Reconcile `signup.button` label — kept `"Passkeyでアカウント作成"` / `"Create Account with Passkey"` and appended `"（30秒）"` / `"(30s)"` to set expectations

## 9. Post-Signup Dialog Refresh

- [x] 9.1 Remove `postSignup.hypeGuideLabel` from both locales
- [x] 9.2 Remove the corresponding hype-guide row from the `PostSignupDialog` component template
- [x] 9.3 Update `postSignup.title` to celebration-first — JA `"🎉 準備完了！ようこそ、あなたのタイムテーブルへ"`; EN `"🎉 You're all set — welcome to your timetable"`. Added a new `postSignup.subtitle` key for the calmer follow-up line ("新しいライブが見つかったら、ここでお知らせします。" / "New lives will show up here as we find them.") rendered in the template + corresponding `.post-signup-subtitle` CSS rule
- [x] 9.4 Notification + PWA rows preserved unchanged
- [x] 9.5 ~~Invert always-visible-Hype-row test assertions~~ — no such assertions existed in either `test/components/post-signup-dialog.spec.ts` (11 tests) or `src/components/post-signup-dialog/post-signup-dialog.spec.ts` (16 tests). The spec requirement was unenforced; deleting the i18n key + template row is the entire change. All 27 tests pass unchanged after the row removal

## 10. Empty / Error Microcopy

- [x] 10.1 Update `dashboard.empty.title` and `dashboard.empty.subtitle` to express a promise — JA title `"新しいライブが見つかり次第、ここに並びます"`, subtitle `"もっと推しを増やすと、タイムテーブルが充実します。"`; EN parallel
- [x] 10.2 Update `discovery.noResults` with romaji/spelling hint — JA `"アーティストが見つかりません — 英語名やローマ字でも試せます"`; EN `"No artists found — try alternate spellings or romaji"`
- [x] 10.3 Two-tone error split applied:
  - **Network tone** (5 keys, both locales): `welcome.error.login`, `signup.error`, `discovery.followFailed`, `discovery.searchFailed`, `settings.resendError` — all rewrap with explicit network-instability framing and "少し時間を置いてもう一度お試しください" / "Wait a moment and try again"
  - **Transient tone** (kept brief): `welcome.error.navigation`, `settings.signOutError` — left close to existing copy since these are local-action failures, not network

## 11. Verification

- [x] 11.1 `make lint` green (Biome + stylelint + typecheck + brand-vocabulary) — confirmed via `make check` output
- [x] 11.2 `make check` green — 1028 tests pass, coverage thresholds met
- [ ] 11.3 Manual smoke pass in `npm start` — **deferred to PR review**: dev server smoke is the user's responsibility before merge; copy-only change with full test suite + lint coverage gives high confidence
- [x] 11.4 `openspec validate refine-onboarding-copy --strict` passes

## 12. Pull Requests

- [x] 12.1 Open PR in `specification/` containing this change folder + spec deltas — liverty-music/specification#434
- [x] 12.2 Open PR in `frontend/` — liverty-music/frontend#350
- [x] 12.3 Cross-link the two PRs
- [x] 12.4 ~~Per-screen commits~~ — collapsed to a single commit. translation.json is shared across all 9 modification groups and partial-staging it would have required `git add -p` gymnastics with little reviewer benefit. The PR description mirrors the per-area structure
- [ ] 12.5 After both PRs merge, archive with the same manual delta-sync pattern used for `establish-brand-vocabulary` (see archive PR #432 for template)

## 13. Welcome Hero Visual Refinement (post-initial review iteration)

After landing the initial copy refresh in PR #350, design review surfaced several visual issues the copy alone could not address. This section captures the visual polish round.

- [x] 13.1 Drop the `welcome.hero.descriptor` introduction — duplicated the subtitle's mechanism explanation. Brand → title → subtitle is a tighter hierarchy
- [x] 13.2 Rewrite title from `"もう二度と見逃さない"` to `"絶対に見逃さない"` — eliminates `もう` echo with the subtitle's `もう終わり`
- [x] 13.3 Restructure subtitle as 2-line `subtitlePain` + `subtitleAction` keys to allow distinct paragraph treatment without HTML in i18n
- [x] 13.4 Apply festival-spotlight glow vocabulary (`text-shadow` reusing `event-card[data-matched]` pattern) to:
  - `welcome-brand` — ブランドが視覚階層の最上位として光る
  - `welcome-subtitle-action strong` — 強調動詞 `追う` / `行く` / `tracks` / `go` がブランドの声として浮かぶ
- [x] 13.5 Embed `<strong>` tags in `welcome.hero.subtitleAction` and bind via `t="[html]..."` so emphasis lives in HTML semantic markup, not slot composition
- [x] 13.6 Apply `text-wrap: balance` + `word-break: auto-phrase` to `.welcome-title`, `.welcome-subtitle`, `.welcome-preview-label` for phrase-aware CJK line breaks
- [x] 13.7 `welcome-hero` height: `95svh` → `100svh` (eliminates the awkward 5svh peek that caught either preview-label text or stage headers; the explicit scroll CTA covers the affordance)
- [x] 13.8 Bump margins for breathing room: `.welcome-title` `space-s → space-m`, `.welcome-subtitle` `space-2xs → space-xs` + `line-height: relaxed`, `.welcome-subtitle-action` `space-l → space-xl`, `.welcome-brand` font-size `step-0 → step-2`, `line-height: snug` on title
- [x] 13.9 Drop leading `↓` from `welcome.hero.seePreview` i18n value — CSS `::after` already adds the trailing arrow, leading caused duplication

## 14. Page-Help Redesign

`<page-help>` was a plain text dump; refined into a proper info dialog with semantic structure and visible hierarchy.

- [x] 14.1 Add `<header>` wrapping a `<svg-icon name="info">` + `<h2>` title with a subtle bottom divider — anchors the dialog with a visual entry point
- [x] 14.2 Bullet markers (`▸` in `--color-brand-accent`) for `.page-help-tips` items so tips read as advice, not generic copy
- [x] 14.3 Lane block (HOME/NEAR/AWAY in dashboard help): convert `<ul><li>` to `<dl><dt><dd>` (semantic definition list) + CSS grid `grid-template-columns: auto 1fr` so descriptions align in a flush-left column regardless of label width. Drop leading `—` from the description i18n values (column gap replaces it)
- [x] 14.4 Embed an inline genre-chip demo (`Rock` / `Pop` (active) / `Jazz`) in the discovery help — show the actual UI primitive instead of just describing it. CSS mimics `.genre-chip` rules from discovery-route via local `--_white-*` tokens for design coherence
- [x] 14.5 Hype table (My Artists help): add row separators (`tr + tr` border-block-start) for clearer scanning
- [x] 14.6 `.page-help-trigger` (the `?` button): brand-accent border + tinted background, instead of muted color — discoverable as a tappable affordance not a disabled chip

## 15. Bottom-Sheet / Nav / State-Placeholder Polish

App-wide visual primitives that the page-help work surfaced as needing attention.

- [x] 15.1 `bottom-sheet`: bump `.handle-bar` bottom padding `space-3xs → space-xs` so all sheets get a baseline gap between handle and content (fixes user-home-selector's previously cramped header without disrupting sheets that already added their own top padding)
- [x] 15.2 `user-home-selector.css`: add `padding-block-start: var(--space-m)` to `.selector-content` — was missing, causing the title to crash into the handle
- [x] 15.3 `bottom-nav-bar`: strengthen active-tab treatment with a 3-layer cue — brand-accent color (existing) + `font-weight: 700` on `.nav-label` + 2px `::before` accent bar at the top edge of the active tab. "Current page" now reads instantly
- [x] 15.4 `page-header`: page title font-size `step-1 → step-2`, `font-weight: normal → 600` — page identity now visually weighted vs. nav labels
- [x] 15.5 `page-header` is rendered unconditionally in `my-artists-route.html` (was hidden when `artists.length === 0`, leaving the empty state without a page identity)
- [x] 15.6 `state-placeholder`: switch icon color from `--color-text-muted` to `--color-brand-accent` so the empty-state icon reads as "promised / waiting" instead of "broken / forgotten". Increase wrapper gap `space-2xs → space-s` for breathing room
- [x] 15.7 `svg-icon` global fix: add `.svg-icon[fill="none"] { fill: none }` rule. The global reset (`:where(svg) { fill: currentcolor }`) was overriding each SVG's `fill="none"` attribute (presentation attributes lose to even zero-specificity CSS), causing all stroked Lucide icons (clock, music, info, etc.) to render as filled disks. **Visible app-wide impact** — every icon that uses `fill="none"` now renders as the intended outline
- [x] 15.8 Nav rename: `nav.home` JA/EN value `"Home"` → `"Timetable"`. Both consumers (bottom-nav label + dashboard page-header title) update via the single i18n value change. The dashboard route stays at `/dashboard` (internal name); the user-facing label aligns with the brand vocabulary established by the welcome page
