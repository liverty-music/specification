## 1. JA copy refinement — retire "推し" in onboarding surfaces

- [x] 1.1 In `frontend/src/locales/ja/translation.json`, update `welcome.cta.getStarted` from `"推しを選んでみる"` to `"アーティストをフォローする"`.
- [x] 1.2 Update `welcome.preview.label` from `"↓ 推しを選ぶと、あなただけのタイムテーブルに！"` to `"↓ アーティストをフォローすると、あなただけのタイムテーブルに！"`.
- [x] 1.3 Update `signup.title` from `"あと一歩で、推しのライブを逃さなくなる"` to `"あと一歩で、好きなアーティストのライブを逃さなくなる"`.
- [x] 1.4 Update the onboarding popover guide string `discovery.popoverGuide` so that `選んだ推しのライブが` becomes `フォローしたアーティストのライブが` (preserve the rest of the sentence verbatim).
- [x] 1.5 Update the onboarding subtitle near `translation.json:144` from `"もっと推しを増やすと、タイムテーブルが充実します。"` to `"もっとアーティストをフォローすると、タイムテーブルが充実します。"`.
- [x] 1.6 Grep `frontend/src/` (excluding `node_modules`, `dist`, `.git`) for any remaining `推し` occurrences in JA copy or comments and resolve each one (either replace with the canonical pair or, if it is a legitimate non-user-facing reference, leave a brief code comment).
- [x] 1.7 Run `make lint` in `frontend/` and confirm `brand-vocabulary` lint passes; if the lint script supports an absolute banned-term check, ensure `推し` is on the banned list (otherwise note as a follow-up).

## 2. Discovery snack copy correction

- [x] 2.1 In `frontend/src/locales/ja/translation.json`, update `discovery.hasUpcomingEvents` from `"{{name}}のライブが近日開催予定です！"` to `"{{name}}の開催予定のライブが見つかりました！"`.
- [x] 2.2 Decide whether to mirror the rewording in `frontend/src/locales/en/translation.json` (current EN says "upcoming concerts" already, but verify the phrasing reads as "found" not "imminent"); update if needed.

## 3. Coach mark dismissal — switch to tap-only

- [x] 3.1 In `frontend/src/routes/discovery/discovery-route.ts`, delete the `COACH_MARK_FADE_MS` module constant (currently `const COACH_MARK_FADE_MS = 2000`).
- [x] 3.2 Delete the `coachMarkFadeTimer` field from the `DiscoveryRoute` class.
- [x] 3.3 In the `onShowDashboardCoachMarkChanged` handler, delete the `setTimeout(...)` block that calls `deactivateSpotlight()` and remove the assignment `this.coachMarkFadeTimer = ...`.
- [x] 3.4 In `detaching()`, delete the `if (this.coachMarkFadeTimer) { clearTimeout(...); this.coachMarkFadeTimer = null }` block. The existing `detaching()` cleanup that calls `deactivateSpotlight()` (per `onboarding-spotlight` route-detach requirement) SHALL remain.
- [x] 3.5 Verify by reading the route file once edited that no reference to `COACH_MARK_FADE_MS` or `coachMarkFadeTimer` remains.
- [x] 3.6 Run `make lint` and `make test` (vitest) in `frontend/` and ensure both pass.
- [x] 3.7 Manually verify (via dev server + onboarding flow) that the Discovery → Dashboard coach mark stays visible indefinitely and dismisses cleanly only when the highlighted Dashboard icon is tapped. (Live-browser flow N/A — dev env intentionally stopped and the local app gates on offline Zitadel/backend. Verified instead by: merged PR #364 + green CI, full local vitest pass (1091), and source review confirming zero `COACH_MARK_FADE_MS`/`coachMarkFadeTimer` references remain in `discovery-route.ts`.)

## 4. User home selector — copy + back button

- [x] 4.1 In `frontend/src/locales/ja/translation.json`, update `userHome.description` from `"HOME STAGEにはあなたの地元のライブが並びます。居住エリアはどこですか？"` to `"HOME STAGEには選択したエリアのライブが並びます。あなたの居住エリアはどこですか？"`.
- [x] 4.2 If `frontend/src/locales/en/translation.json` carries an equivalent EN value for `userHome.description`, update it to mirror the structure ("HOME STAGE shows concerts in the area you select. Which area do you live in?" or similar).
- [x] 4.3 Add a new key `userHome.backToRegions` to both `ja` and `en` translation files. JA value: `"地方一覧"`. EN value: `"Regions"` (or equivalent short noun).
- [x] 4.3a Remove the now-deprecated `userHome.back` key from both `ja` and `en` translation files. The previous canonical spec listed it for the back control's `aria-label`; the modified spec drops it entirely (visible label is the sole accessible name per WCAG 2.5.3). No remaining references in `frontend/src/`.
- [x] 4.3b Acknowledge `userHome.selectPrefecture` in the modified spec's i18n key list. The key already exists in both `ja` and `en` translation files (added in `997cda6` "feat(i18n): add i18n infrastructure"); this change merely formalizes it in `openspec/specs/user-home/spec.md`'s key inventory — no code change required.
- [x] 4.4 In `frontend/src/components/user-home-selector/user-home-selector.html`, modify the Step 2 back button so it renders BOTH the chevron `<svg>` icon AND a `<span t="userHome.backToRegions">` text label. Do NOT bind `aria-label`; the visible label is the accessible name (per WCAG 2.5.3). Mark the chevron SVG `aria-hidden="true"`.
- [x] 4.5 In `frontend/src/components/user-home-selector/user-home-selector.css`, update `.selector-back-btn` so it is a pill-shaped button (`inline-size: auto`, padding tuned to display icon + text inline) rather than a 2rem circle. Keep the existing border-radius behavior or adjust to `var(--radius-button)` for consistency with `.selector-btn`.
- [x] 4.6 Verify the chevron SVG remains visible (sufficient stroke contrast); if necessary, switch the SVG color from `--color-text-secondary` to `--color-text-primary` so the icon reads clearly alongside the text.
- [x] 4.7 Smoke-test the home selector via the dev server: open from Dashboard (onboarding) and Settings; confirm the back button is visually obvious and behaves the same way as before (returns to Step 1). (Live-browser flow N/A — dev env intentionally stopped. Verified instead by: merged PR #364 + green CI, full local vitest pass, and source review confirming the back control renders the chevron `<svg aria-hidden="true">` alongside `<span t="userHome.backToRegions">` with the pill-shaped `.selector-back-btn` CSS.)

## 5. Concert detail sheet — JA/EN i18n

- [x] 5.1 Add a new top-level `eventDetail` namespace to `frontend/src/locales/ja/translation.json` and `frontend/src/locales/en/translation.json` containing keys: `ariaLabel`, `openStart`, `openInGoogleMaps`, `ticketStatus`, `stopTracking`, `viewOfficialInfo`, `addToCalendar` (use the JA/EN values from the design table). The em-dash fallback is locale-invariant and supplied directly by the ViewModel, not through an i18n key.
- [x] 5.2 Add a sub-namespace `eventDetail.journeyStatus` to both locale files with entries for every value of the `TicketJourneyStatus` enum (`tracking`, `applied`, `lost`, `unpaid`, `paid`). Note: the frontend currently exposes this concept as a local TS string-literal union named `JourneyStatus`; the canonical concept name from `openspec/specs/ticket-journey` is `TicketJourneyStatus`.
- [x] 5.3 In `frontend/src/components/live-highway/event-detail-sheet.html`:
  - Replace the literal `aria-label="Event details"` on the `<bottom-sheet>` element with a binding to `eventDetail.ariaLabel`.
  - Replace the literal `Open ${event.openTime || '—'} / Start ${event.startTime}` line with an i18n call using key `eventDetail.openStart` and `{{open}}`, `{{start}}` interpolation. Supply the `{{open}}` value via a VM getter (e.g. `openTimeOrFallback`) that returns `event.openTime ?? '—'`; do not introduce a separate i18n key for the fallback character.
  - Replace `Open in Google Maps` link text with `t="eventDetail.openInGoogleMaps"`.
  - Replace `Ticket Status` heading with `t="eventDetail.ticketStatus"`.
  - Replace `Stop tracking` button label with `t="eventDetail.stopTracking"`.
  - Replace `View Official Info` link text with `t="eventDetail.viewOfficialInfo"` (keep the `<svg-icon>` adjacent to the localized text).
  - Replace `Add to Calendar` link text with `t="eventDetail.addToCalendar"`.
- [x] 5.4 In the `repeat.for="s of journeyStatuses"` `<button>` and any other rendering site that displays a raw `TicketJourneyStatus` string (typed as `JourneyStatus` in the frontend TS code today), replace `${s}` with a localized lookup that resolves `eventDetail.journeyStatus.<s>` via the same `t` mechanism (e.g. `<span t.bind="'eventDetail.journeyStatus.' + s"></span>`).
- [x] 5.5 If the currently-displayed `event.journeyStatus` is rendered anywhere outside the button list, apply the same `eventDetail.journeyStatus.<value>` localization there.
- [x] 5.6 Run `make lint` (which includes brand-vocabulary parity check) and confirm `eventDetail.*` keys are present in both locales.
- [x] 5.7 Run `make test` (vitest) and resolve any failing unit test that asserts on the previous literal English text in the detail sheet.
- [x] 5.8 Smoke-test the detail sheet via the dev server in JA locale: open a concert card, confirm every visible string is Japanese, including journey-status buttons. (Live-browser flow N/A — dev env intentionally stopped. Verified instead by: merged PR #364 + green CI, full local vitest pass including `check-brand-vocabulary` (i18n key parity) and `ticket-journey-mapper`, and source review confirming all sheet strings bind to `eventDetail.*` keys incl. `eventDetail.journeyStatus.<s>`.)

## 6. Test updates

- [x] 6.1 Audit `frontend/tests/**/*.spec.ts` and `frontend/src/**/*.stories.ts` for hardcoded JA strings affected by tasks 1.x, 2.1, 4.1, 4.3; update assertions to match the new copy.
- [x] 6.2 Audit Playwright E2E tests under `frontend/tests/e2e` (if present) for selectors that look up the home selector back button, the Discovery coach mark, or the concert detail sheet by literal text; update them to use the new copy or to use stable `data-*` selectors instead.
- [x] 6.3 Confirm `make check` (frontend) passes — i.e., `make lint` and `make test` both succeed.

## 7. Specification archival prep

- [x] 7.1 Confirm `openspec status --change refine-onboarding-copy --json` shows `isComplete: true` (all tasks ticked) before invoking `/opsx:archive`.
- [x] 7.2 Open the specification PR for this change with the standard Conventional Commit message linking the tracking issue (`Refs: #348`).
