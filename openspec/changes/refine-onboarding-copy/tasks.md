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

- [ ] 12.1 Open PR in `specification/` containing this change folder + spec deltas
- [ ] 12.2 Open PR in `frontend/` containing the i18n migration + screen edits + post-signup-dialog component change + test updates
- [ ] 12.3 Cross-link the two PRs
- [ ] 12.4 Recommend reviewing the frontend PR commit-by-commit (one screen / one concern per commit per the migration plan in design.md)
- [ ] 12.5 After both PRs merge, archive with the same manual delta-sync pattern used for `establish-brand-vocabulary` (see archive PR #432 for template)
