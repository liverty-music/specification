## Why

The My Artists page help sheet currently introduces a term ("Stage") that appears nowhere else in the UI, mixes two unrelated topics (hype level mechanics + long-press unfollow) in a single visual lane, and leaves the hype-level table with ragged column edges because icon + label share one cell. Compounding this, the per-artist hype default is currently `watch` (no notifications), which makes the entire notification model an opt-in that users must discover through trial — a friction point that has measurably depressed engagement during preview testing. Finally, the canonical hype tier surface labels are translated to Japanese in some surfaces (`観測 / 地元 / 近郊 / 全国`) but rendered as invariant English in others (e.g. the Dashboard timetable lanes, the help sheet's own hype table), so users see the same concept under two different vocabularies depending on which page they are looking at.

This bundle refines the my-artists help-sheet copy and structure, unifies the hype vocabulary so the same surface words appear everywhere a hype value is shown, switches the per-follow default to `nearby` so guest users encounter the notification value-proposition immediately, and restructures the signup-prompt-banner so it is persistently visible (and non-dismissable) for guests across the onboarding-completion threshold.

## What Changes

### Hype vocabulary (brand-vocabulary capability)

- **BREAKING (copy)**: Retire `Stage` as a Japanese-locale alias for the Hype concept. The hype label SHALL be `Hype` in both JA and EN. The Japanese supplement word `熱量` SHALL appear only as a parenthetical gloss inside the my-artists help-sheet description, not as the canonical entity label.
- **BREAKING (copy)**: Promote the four hype tier surface forms (`Watch`, `Home`, `Nearby`, `Away`) from Layer A (entity-grounded, locale-translatable) to Layer B (brand expressions, locale-invariant English). The JA-only forms `観測 / 地元 / 近郊 / 全国` SHALL be removed from `entity.hype.values.*`.
- The `entity.hype.label` and `entity.hype.values.*` keys SHALL be removed from `entity.*` namespace; the lint script that enforces JA/EN parity on `entity.*` SHALL no longer apply to these keys.
- Update the brand-vocabulary registry to record `Hype`, `Watch`, `Home`, `Nearby`, `Away` as Layer B invariant brand expressions. Remove the prior scenario stating "`entity.hype.label` MAY be `Stage` in JA".

### Default hype tier (my-artists + passion-level capabilities; backend coordination)

- Change `DEFAULT_HYPE` constant in `frontend/src/entities/follow.ts` from `'watch'` to `'nearby'`.
- **Backend coordination**: add a new Atlas migration in the backend repo (`backend/k8s/atlas/base/migrations/`) that runs `ALTER TABLE "followed_artists" ALTER COLUMN "hype" SET DEFAULT 'nearby'`. This is required because the `Follow` RPC has no `hype` field — the column default is the only mechanism that determines a fresh follow's hype value on the backend. Without the backend change, an authenticated user's new follow would silently revert to `watch` on the next `ListFollowed` response despite the frontend's stated default.
- All new follows (guest and authenticated) SHALL receive `nearby` as the starting hype value, communicating that "by default, we will notify you about concerts within reach."
- Guest-data merge logic SHALL continue to suppress merging follows that match the new default value (so that an authenticated user's existing `nearby` setting is not overwritten by a guest record that simply held the default). With backend and frontend defaults aligned at `nearby`, this suppression is consistent.

### My Artists page hype column header (my-artists capability)

- Remove the `<small t="entity.hype.values.*">` translation bindings from the `.hype-col-header` cells in the artists table.
- Render the four tier labels as the invariant English brand expressions `Watch / Home / Nearby / Away` directly in the template.

### Multi-section help-sheet structure (onboarding-page-help capability)

- **BREAKING (structure)**: Remove the per-sheet single `<h2 class="page-help-title">` heading. The bottom-sheet's `aria-label` ("ページのヘルプ" / "Page help") SHALL be the sheet's accessible name.
- Each help sheet SHALL be composed of one or more `<section>` blocks, each prefixed by a `<h3 class="help-section-title">` (icon + title + bottom border, reusing the visual pattern formerly carried by `.page-help-header` + `.page-help-title`).
- The `.page-help-title` CSS class SHALL be replaced by `.help-section-title`. The `.page-help-header` CSS class is retained as the section-title row wrapper (icon + heading + divider).
- The Discovery help sheet SHALL split into two sections:
  - `アーティストの探し方` / `Finding Artists` (carries the existing description, chip demo, and the two genre/search tips)
  - `フォロー解除` / `Unfollowing` (one-line pointer to the My Artists page)
- The Dashboard help sheet SHALL split into two sections:
  - `ステージレーンの読み方` / `Reading the Stage Lanes` (carries the existing description + HOME/NEAR/AWAY explanation list)
  - `ライブ詳細を見る` / `Viewing Concert Details` (carries the existing card-tap tip)
- The My Artists help sheet SHALL split into two sections:
  - `Hype（熱量） について` / `About Hype` (carries the Hype description, the 3-column tier table, and the Away-recommendation tip)
  - `フォロー解除` / `Unfollowing` (carries the long-press tip; this section is rendered only when the device is pointer-coarse, matching the existing `if.bind="isPointerCoarse"` gate)

### Hype-level table refinement (onboarding-page-help capability)

- The help-sheet hype tier table SHALL render as a 3-column CSS Grid:
  1. **Icon column** (`auto` width, centered): `👀 / 🔥 / 🔥🔥 / 🔥🔥🔥`
  2. **Label column** (`auto` width, start-aligned): `Watch / Home / Nearby / Away` (invariant English)
  3. **Description column** (`1fr` width, start-aligned): notification-scope description
- Replace the existing `<table class="page-help-hype-table">` markup with a semantic `<dl>` (definition list) using CSS Grid for alignment, or retain `<table>` markup if the rendering pattern from `.page-help-lanes` (already 2-col grid) extends cleanly to 3 columns. Final markup choice deferred to design.md.

### Help-sheet copy updates (onboarding-page-help capability)

- `pageHelp.myArtists.title` (JA): `Stage について` → `Hype（熱量） について`
- `pageHelp.myArtists.title` (EN): `About Hype Levels` → `About Hype`
- `pageHelp.myArtists.description` (JA): `Stage で通知の範囲が変わります。ドットをタップして切り替えられます。` → `Hype（熱量） で通知の範囲が変わります。スライダーをタップして切り替えられます。`
- `pageHelp.myArtists.description` (EN): `Hype level controls how far away you get notified. Tap a dot to change it.` → `Hype controls how far away you get notified. Tap the slider to change it.`
- `pageHelp.myArtists.awayDesc` (JA): `全国のライブを通知` → `全てのライブを通知`
- `pageHelp.myArtists.awayDesc` (EN): `Notify for all lives nationwide` → `Notify for every concert`
- `pageHelp.myArtists.homeDesc` (EN): `Notify for home area lives` → `Notify for home-area concerts` (consistency — "lives" was a Japanism)
- `pageHelp.myArtists.nearbyDesc` (EN): `Notify for nearby lives too` → `Notify for nearby concerts too` (same)
- `pageHelp.myArtists.tip` (JA): `まずは気になるアーティストを Home に設定してみましょう。近くでライブがあればお知らせします。` → `遠征してでも見たいアーティストは Away に設定してみましょう！`
- `pageHelp.myArtists.tip` (EN): `Start by setting artists you're curious about to Home — you'll get notified when they play nearby.` → `Set artists you'd travel for to Away to never miss them!`
- `pageHelp.myArtists.longPressTip` and `pageHelp.dashboard.cardTip` retain their current copy but move into their own dedicated sub-section.
- Seven new keys SHALL be introduced — six sub-section titles (one per `<section>` across the three help sheets) and one new descriptive copy key for the Discovery unfollow sub-section:
  - `pageHelp.discovery.findingSectionTitle`
  - `pageHelp.discovery.unfollowSectionTitle`
  - `pageHelp.discovery.unfollowDesc` (new descriptive copy: JA `フォロー解除は My Artists ページから行えます。` / EN `You can unfollow from the My Artists page.`)
  - `pageHelp.dashboard.lanesSectionTitle`
  - `pageHelp.dashboard.detailsSectionTitle`
  - `pageHelp.myArtists.hypeSectionTitle`
  - `pageHelp.myArtists.unfollowSectionTitle`

### Signup-prompt-banner persistence (signup-prompt-banner capability)

- **BREAKING (UI)**: Remove the dismiss `X` button from the banner template entirely. The banner SHALL no longer accept user dismissal.
- Remove the `banner-dismissed` custom event from the `SignupPromptBanner` component contract.
- Remove the `onBannerDismissed()` handler usages from page hosts (`my-artists-route.ts`, dashboard route) — the banner's `visible` binding now reflects authentication + page state only, not a user-controlled dismissed flag.
- The banner SHALL be displayed on My Artists for any guest user (`!isAuthenticated`) regardless of onboarding state — both during the my-artists onboarding step AND after onboarding completion.
- The banner SHALL continue to be displayed on Dashboard for guests only AFTER onboarding completion (the onboarding-tutorial popover guidance already occupies dashboard attention during onboarding).
- Banner copy (JA: `フォロー情報を保存してコンサート通知を受け取ろう！` / EN: `Save your followed artists and get concert notifications.`) is unchanged. The semantic shift in default hype (now Nearby) implicitly raises the banner's relevance without needing wording changes.

## Capabilities

### New Capabilities
<!-- No new capabilities. -->

### Modified Capabilities

- `brand-vocabulary`: Retire `Stage` as a JA alias for the Hype concept; promote the four hype tier surface forms (`Watch / Home / Nearby / Away`) from Layer A (entity-grounded) to Layer B (invariant brand expressions); update the asymmetric-locale scenario; update the registry table.
- `my-artists`: Change `DEFAULT_HYPE` from `watch` to `nearby`; replace the `entity.hype.values.*`-bound `<small>` elements in the artists-table column headers with direct invariant English text.
- `onboarding-page-help`: Restructure each help sheet (Discovery, Dashboard, My Artists) into multiple `<section>` blocks each titled by `<h3 class="help-section-title">`; remove the single per-sheet `.page-help-title`; refine the my-artists hype tier table into a 3-column grid (icon / label / description); update copy keys for the my-artists sheet (title, description, awayDesc, tip).
- `signup-prompt-banner`: Remove the dismiss `X` button entirely; change the my-artists banner-visibility trigger so it appears for any guest user (both during and after onboarding), not only after a hype change post-completion.
- `passion-level`: Change the "Default hype level on follow" scenario from `Watch (HYPE_TYPE_WATCH)` to `Nearby (HYPE_TYPE_NEARBY)` to reflect the new column default. Update the "UI labels use locale-appropriate phrasing" scenario so that hype tier labels are invariant English (`Watch / Home / Nearby / Away`) in both locales, removing the JA-only emotion-based labels (`チェック / 地元 / 近くも / どこでも！`). Update the Passion Level Tiers table accordingly.

## Impact

- **Frontend code**:
  - `frontend/src/entities/follow.ts` — change `DEFAULT_HYPE` constant value.
  - `frontend/src/locales/ja/translation.json` and `.../en/translation.json` —
    - Remove `entity.hype.label`, `entity.hype.values.*` keys (or keep `entity.hype` empty if the lint script requires the namespace to exist).
    - Update `pageHelp.myArtists.title`, `pageHelp.myArtists.description`, `pageHelp.myArtists.awayDesc`, `pageHelp.myArtists.tip` per the copy list above.
    - Add `pageHelp.{discovery,dashboard,myArtists}.*SectionTitle` keys.
  - `frontend/src/components/page-help/page-help.html` — restructure all three `<section case="…">` blocks to use the multi-section pattern with `.help-section-title`; replace the hype-table markup with a 3-column grid.
  - `frontend/src/components/page-help/page-help.css` — rename `.page-help-title` → `.help-section-title`; redefine the hype tier list as a 3-column CSS Grid; drop or repurpose `.page-help-hype-table` rules.
  - `frontend/src/routes/my-artists/my-artists-route.html` — replace `<small t="entity.hype.values.*">…</small>` with invariant English label text inside `.hype-col-header` cells.
  - `frontend/src/routes/my-artists/my-artists-route.ts` — adjust `showSignupBanner` trigger so the banner is visible for any guest user on my-artists (loading() sets it true unconditionally when `!isAuthenticated`).
  - `frontend/src/components/signup-prompt-banner/signup-prompt-banner.html` — remove the dismiss button markup.
  - `frontend/src/components/signup-prompt-banner/signup-prompt-banner.ts` — remove `onDismiss()` method and the `banner-dismissed` custom event.
  - `frontend/src/components/signup-prompt-banner/signup-prompt-banner.css` — drop `.signup-banner-dismiss` selector rules.
  - Any host components that wired `banner-dismissed.trigger="onBannerDismissed()"` — strip the binding and the host handler.
  - Brand-vocabulary lint script — update curated entity-stem list to NOT expect `hype` as a translated-namespace entry; add `Hype / Watch / Home / Nearby / Away` to the Layer B canonical-form registry if the script consults it.
- **Backend code change**: one new Atlas migration file under `backend/k8s/atlas/base/migrations/` (single-statement `ALTER TABLE … SET DEFAULT 'nearby'` plus the matching `COMMENT ON COLUMN` update). Add the new migration file to `backend/k8s/atlas/base/kustomization.yaml` under `configMapGenerator.files`. No Go source edits required.
- **No proto / RPC contract changes.** The `HypeType` enum is unchanged; the `Follow` RPC signature (no `hype` field) is unchanged.
- **No data migration of existing records.** Existing followed-artist rows keep their stored hype values; only newly-created follows pick up the new default. The DB-default change is purely forward-looking — it does not run `UPDATE … SET hype='nearby' WHERE hype='watch'`.
- **Breaking changes**:
  - **Copy/i18n**: `entity.hype.label`, `entity.hype.values.*` keys are removed — any test that asserts on translated hype labels (e.g. `観測`) will break and SHALL be updated to assert on the invariant English forms.
  - **UI behavior**: The signup banner can no longer be dismissed by guests on My Artists. Behavior-asserting Playwright tests that close the banner via the X button MUST be rewritten.
- **Tests**: Vitest unit tests in `frontend/src/components/page-help/page-help.spec.ts`, `frontend/src/routes/my-artists/**`, and `frontend/src/components/signup-prompt-banner/**` will need assertion updates. Playwright E2E flows that traverse the my-artists help sheet by literal text need to use the new copy or stable `data-*` selectors. The brand-vocabulary lint script's curated-entity list and unit tests should be updated.
