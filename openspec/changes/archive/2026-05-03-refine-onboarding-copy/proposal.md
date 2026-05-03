## Why

The onboarding flow's user-facing copy was audited end-to-end (welcome → discovery → signup → post-signup) and three structural problems surfaced:

- **Terminology drift**: the same concept is named differently in different places (`ライブ` vs `コンサート`, `ダッシュボード` vs `タイムテーブル` vs `ライブカレンダー`, `登録` vs `フォロー`, JA `Hype` everywhere despite never being a JA loanword in fan culture).
- **Cold-start ambiguity**: a stranger landing on `/welcome` cannot tell what Liverty Music *is* (no product descriptor under the brand), and the post-signup screen front-loads a checklist instead of celebrating the moment.
- **Stale user-facing labels**: `Music DNA` (Discovery orb), `チュートリアルお疲れさまでした` (signup gate), and the "always visible Hype guide" in PostSignupDialog are leftovers from earlier iterations that no longer match the product's intended voice.

The `establish-brand-vocabulary` change just landed, providing the `entity.*` namespace and parity lint. This change consumes that infrastructure to deliver the actual content fixes.

## What Changes

- **Populate Layer A registry** with the first concrete entries:
  - `entity.hype.label` → JA `Stage` / EN `Hype` (asymmetric — first real exercise of the namespace's design rule)
  - `entity.hype.values.{watch,home,nearby,away}` → JA `観測 / 地元 / 近郊 / 全国` and EN `Watching / Home / Near / Away` (key segment `nearby` mirrors the TS `Hype` enum value)
  - `entity.concert.label` → `ライブ` / `Concert` (asymmetric — JA canonical fan-vocab term differs from EN noun)
  - `entity.artist.label` → `アーティスト` / `Artist`
  - `entity.homeArea.label` → `ホームエリア` / `Home Area`
- **Migrate existing `hype.*` and screen-local hype text** to the new `entity.hype.*` keys; remove orphaned legacy keys.
- **Unify terminology** in JA copy: `ライブ` (not `コンサート`), `タイムテーブル` (not `ダッシュボード` / `ライブカレンダー` in user-visible contexts), `フォロー` (not `登録`).
- **Welcome hero** ([`welcome-route.html`](frontend/src/routes/welcome/welcome-route.html)): add a one-line product descriptor under the brand; rewrite the primary CTA to predict its reward; promote `welcome.guestFriendly` from below the buttons.
- **Discovery**: drop `discovery.orbLabel` ("Music DNA") entirely; rewrite `discovery.popoverGuide` and `coachMark.viewTimetable` to celebrate the experience instead of merely instructing.
- **Signup gate**: delete `チュートリアルお疲れさまでした`; restructure as value-first ("通知が届く / 端末横断 / 履歴保持") with Passkey as a means, not the lead.
- **Post-Signup Dialog**: **BREAKING** for the `post-signup-dialog` capability — drop the always-visible Hype guide row; lead with celebration; demote notification + PWA to optional power-ups. Hype discoverability is an accepted regression — `myArtists.coachMark.setHype` was never rendered and was deleted in this change; a follow-up can wire a My Artists coach mark if the team judges the regression meaningful.
- **Empty / error microcopy**: turn `dashboard.empty` from a flat statement into a promise; split the boilerplate `失敗しました。もう一度お試しください` into 2 tones (network vs transient).

### Visual polish (added in design review iteration after the initial copy refresh landed)

The copy refresh exposed a number of presentation-layer issues that text alone could not address. Captured here so the change reflects what actually shipped, not a partial truth:

- **Welcome hero visual refinement** — drop the redundant `descriptor` line, rewrite title to eliminate `もう` echo, split subtitle into 2 keys (pain + action) for distinct paragraph treatment, apply a "festival-spotlight" glow vocabulary (reusing `event-card[data-matched]` text-shadow pattern) to the brand wordmark and the role-reversal verbs (`追う`/`行く`/`tracks`/`go`), apply `text-wrap: balance` + `word-break: auto-phrase` for phrase-aware CJK wrapping, switch hero to full-viewport (drop the awkward 5svh peek), and bump margins for breathing room.
- **Page-help dialog redesign** — info icon + title + divider header; bullet markers (`▸` brand-accent) on tip lists; `<dl>` + CSS grid for the dashboard HOME/NEAR/AWAY lane block (descriptions now align in a flush-left column instead of being thrown off by label-width differences); inline genre-chip demo on the discovery help (show the actual UI primitive instead of describing it); brand-accent help trigger so it reads as tappable instead of disabled.
- **Bottom-sheet baseline padding** — bump `.handle-bar` bottom padding so all sheets (user-home-selector, post-signup, page-help, etc.) get a baseline gap between the handle and content.
- **Bottom-nav active state** — 3-layer cue (color + bold label + 2px top accent bar) so the current page reads instantly.
- **Page header polish** — title font-size up + bolder weight; render unconditionally on My Artists (was hidden when empty, breaking page-identity continuity).
- **State-placeholder icon visibility** — switch icon color to brand-accent and fix an app-wide bug where `:where(svg) { fill: currentcolor }` in the global reset overrode each Lucide icon's `fill="none"` attribute, causing all stroked icons to render as filled disks.
- **Nav rename** — `nav.home` value `"Home"` → `"Timetable"` in both locales (route stays `/dashboard`); the user-facing label aligns with the brand vocabulary established by the welcome page.

## Capabilities

### New Capabilities
None. This change is content + minor structural revision; no new system behavior.

### Modified Capabilities
- `frontend-i18n`: add a requirement that legacy top-level namespaces superseded by `entity.*` SHALL be removed from the locale files (no orphaned `hype.*` keys after migration).
- `post-signup-dialog`: REMOVE the "Hype guide hint always visible in PostSignupDialog" requirement and its scenarios; MODIFY the dialog-content requirement to lead with a completion celebration row instead of a checklist.
- `landing-page`: MODIFY `Guest-Friendly Welcome Copy` to allow promoting the no-account-required message into the primary CTA caption rather than restricting it to a position below the buttons.

The `brand-vocabulary` capability is not modified at the spec level — populating `entity.hype.*` is a data change that already conforms to the existing requirements (locale parity, known-entity stems, asymmetric values). No new spec invariant is added.

## Impact

- **specification repo**: 4 spec deltas + this change folder.
- **frontend repo**: rewrites of `src/locales/{ja,en}/translation.json` (move `hype.*` → `entity.hype.*`, retire `discovery.orbLabel`, edit welcome / signup / postSignup / dashboard / discovery copy); minor template adjustments where keys were renamed; PostSignupDialog component change to drop the hype-guide row.
- **No proto changes, no BSR cycle, no backend changes.** The `HypeLevel` enum keeps its proto name; only the JA i18n surface label diverges to `Stage`.
- **CI**: `check-brand-vocabulary` lint script (from `establish-brand-vocabulary`) starts enforcing parity on the populated `entity.*` keys for the first time.
- **No behavior change on the dashboard, discovery RPCs, or auth flows.**
