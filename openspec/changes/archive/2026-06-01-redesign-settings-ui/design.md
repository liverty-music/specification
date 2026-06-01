## Context

The Settings page lives in the `frontend` repo (Aurelia 2 PWA) at `src/routes/settings/settings-route.{html,ts,css}`, with copy in `src/locales/{ja,en}/translation.json`. It follows CUBE CSS (`@layer` + `@scope`) and uses design tokens from `src/styles/tokens.css`.

Current toggle anatomy: each toggle row is a single `<button role="switch">` containing a `.settings-toggle-col` (label + `.settings-row-hint`) on the left and a `.settings-toggle-track` (with an absolutely-positioned `.settings-toggle-thumb`) on the right, laid out with `display:flex; align-items:center; justify-content:space-between`.

Verified defect (Playwright, viewport 412px, real tokens + real CSS): `.settings-toggle-track` has computed `flex-shrink: 1` (no `flex-shrink: 0`), so under the long Japanese consent description it collapses from its declared `2.75rem` (44px) to **20.63px**. The thumb uses a fixed `transform: translateX(1.25rem)` for the ON state, so it ends **21.38px past the (collapsed) track's right edge** and **4.05px past the card's right edge** — matching the "white dot pinned to the card edge, no visible track" symptom in the reported screenshot.

The second analytics toggle (`marketingConsent`) binds to `consent.marketingMeasurement` and is consumed by both the signup consent screen (`src/routes/consent/consent-route.ts`) and the Settings opt-out (`src/routes/settings/settings-route.ts`). The in-flight `introduce-analytics-tool` change (`analytics-consent`) mandates per-purpose toggles and a persistent Settings opt-out. The current Settings label frames this purpose as geography ("海外での分析処理を許可する"), which is a labeling defect, not a redundant control.

## Goals / Non-Goals

**Goals:**

- Toggle track keeps its size and the thumb stays contained, for any description length, on a 412px-class viewport.
- Long consent descriptions are collapsible/expandable with correct switch + disclosure accessibility semantics.
- Consent toggle copy is purpose-based and opt-in friendly; the marketing toggle is relabeled (not removed).
- The guest sign-in/sign-up CTA is a prominent top-of-page hero; authenticated account controls stay at the bottom.
- The iOS sound hint only appears on iOS.
- No regressions to existing Settings behaviors (home area, language, push, sign out) or to the consent state model shared with `consent-route`.

**Non-Goals:**

- No backend, proto, or RPC changes.
- No change to *what* consent data is collected or to the signup consent flow's behavior — only the Settings-page rendering/labeling of existing purposes.
- The cross-border (PostHog/Netherlands) legal disclosure is out of scope here; it remains owned by the signup consent screen and privacy policy.
- Not introducing a full design-system button library (see decision on CTA styling).

## Decisions

### D0. Settings list layout engine: card-grid + row-subgrid (supersedes per-row flex)

The rows were originally independent flex containers that pushed their trailing control to the right edge per-row, so cross-row column alignment was *emergent* — it held only while every row's box model matched exactly. It didn't: the consent rows wrapped the toggle in a `.settings-switch` button whose UA/explicit padding inset the track ~6–8px, and the disclosure split shifted vertical alignment. The toggle misalignment was a symptom of this fragility.

Decision: make `.settings-card` a grid (`grid-template-columns: auto 1fr auto` → lead icon | content | trailing control) and every `.settings-row` a `subgrid` spanning those tracks. Alignment becomes *structural* — icons, labels, and trailing controls snap to shared column lines regardless of each row's content or inner markup. Rows that don't fit the 3-column model (sign-out, volume slider, dividers) opt out via `grid-column: 1 / -1`.

- Per `modern-web-guidance` (css-layout) and `web-design-specialist` (layout-engines): subgrid is Baseline (since 2023-09-15, incl. iOS Safari 16+); the canonical "form labels aligned across fields / ragged-edge card" subgrid pattern is exactly this case. Each `subgrid` line carries an explicit track list above it as a same-cascade fallback.
- a11y: whole-row interactive rows (`<button>`/`<a>`) become the subgrid container themselves (`display: grid; grid-template-columns: subgrid`) — the element keeps its box and role; `display: contents` is avoided (drops the box, historically breaks AT). Split consent rows keep the icon as a direct row child (col1) so no nested subgrid is needed: disclosure → col2, switch → col3.
- A `<button>.settings-row` inherits UA `text-align: center`; since the label is a stretched col2 grid item, the row resets `text-align: start` so labels left-align instead of drifting to the column centre.
- This replaces D1/D2's flex-specific fixes (still valid as defence-in-depth: `flex-shrink: 0` now guards only the in-`.settings-switch` track).

### D1. Fix track sizing with `flex-shrink: 0` + text-column `min-inline-size: 0`

Add `flex-shrink: 0` to `.settings-toggle-track` so it never collapses, and `min-inline-size: 0` to the text column so it absorbs the remaining width and wraps instead of starving the track. Switch the row to `align-items: flex-start` for toggle rows so the control aligns to the first line.

- *Alternative considered*: give the track an explicit `flex-basis`/`min-inline-size` only. Rejected — `flex-shrink: 0` is the direct, intent-revealing fix and is the actual missing declaration; the text column still needs `min-inline-size: 0` to wrap correctly.

### D2. Stop double-purposing `.settings-row-hint`'s indent

`.settings-row-hint` carries `margin-inline-start: var(--space-l)` to align icon-less hints under a label. Inside the toggle column this indent compounds the width starvation. Decouple the toggle description's styling from the icon-alignment hint (separate class / no inherited inline-start margin) so the description can use the full column width.

### D3. Split the switch row into disclosure + switch siblings

To make the description expandable without nesting interactive elements inside a `role="switch"` button, restructure the row into two sibling controls:

- a disclosure `<button aria-expanded>` wrapping the label + collapsible description + chevron, and
- the `<button role="switch" aria-checked>` for the track/thumb.

The chevron only renders when a collapsible description exists. The switch's activation target gets vertical padding so the tap target reaches ≥44px in the block dimension even though the visible track is 24px tall.

- *Trade-off*: the generous "tap anywhere on the row toggles the switch" behavior is lost; tapping the text area now expands rather than toggles. This is the unavoidable cost of accessible disclosure semantics and is acceptable for a low-frequency settings control.
- *Alternative considered*: a tooltip/popover `(i)` button instead of inline expand. Rejected — inline disclosure keeps the explanation in context and avoids an extra overlay primitive.

### D4. Relabel marketing toggle to its purpose; keep it visible

Change `settings.analytics.crossBorderLabel`/`crossBorderDescription` (and the `en` mirror) to describe ad-effectiveness measurement. Keep the toggle bound to `marketingMeasurement`. Do not add a domestic/overseas region switch.

Proposed JA copy (subject to `brand-vocabulary` lint):
- Section: keep `プライバシーと分析`.
- Analytics: label `使い心地の改善に協力する`; desc `「どこで迷いやすいか」を匿名データから見つけ、次のアップデートに活かします。個人を特定する情報は集めません。`
- Marketing: label `広告効果の測定に協力する`; desc `広告から来てくれた人の動きを匿名で測り、届け方の改善に役立てます。オフにしても他の機能には影響しません。`

- *Rationale*: aligns the Settings rendering with the `analytics-consent` per-purpose model and removes a misleading geographic framing that could be read as "turning this off stops domestic processing too" (domestic processing is not optional and not what this toggle controls).

### D5. Guest hero placement and styling

Render a guest-only hero (`if.bind="!auth.isAuthenticated"`) at the top of `.settings-scroll`, before the preferences section. Visual emphasis via a brand-tinted surface (`oklch(from var(--color-brand-primary) l c h / ~12%)` background, `~30%` brand border) with a filled primary `ログイン` button and a ghost/text `新規登録` action. The bottom ACCOUNT section keeps authenticated-only controls; the guest branch of that section is removed (its CTA moves to the hero). Remove the orphan `.settings-guest-prompt` class.

CTA button styling decision: **scope the CTA styles to the settings route for now** rather than introducing a shared button primitive, because no reusable primary-button class exists and a design-system button is a larger, separate effort. Leave a note so a future shared primitive can absorb it. *(Open question O1 if the team prefers the primitive now.)*

New/updated copy: heading `ログインして、もっと便利に`; body `お気に入りと通知を、どの端末でもそのまま使えます` (also resolves the awkward double-を in the current `guestPrompt`).

### D6. iOS-only sound hint

Gate `settings.soundEffectsHint` behind an iOS platform check computed in the ViewModel (e.g. a small `isIOS` derived from the user agent / platform), exposed as a bindable used with `if.bind`. Keep the hint string iOS-specific.

- *Alternative considered*: generalize the wording to drop the iOS reference. Rejected as the weaker option — the hint exists specifically to explain iOS silent-mode behavior; showing it elsewhere is noise, and a generic version loses the informational value.

## Risks / Trade-offs

- [Visual regression baselines] The toggle, hero, and copy changes will alter `e2e/visual/settings.auth.visual.spec.ts` snapshots → intentional; regenerate baselines per the project's main-branch visual-baseline refresh process (delete stale baseline artifacts to force regen).
- [Shared consent state] `marketingConsent`/`analyticsConsent` are shared with `consent-route` via the consent service → only labels/markup change here; the binding fields and persistence stay identical to avoid touching the signup flow.
- [iOS detection fragility] UA/platform sniffing is imperfect → keep the check narrow and defaulting to "hide the iOS hint" when uncertain, so non-iOS never sees iOS-only noise.
- [Tap-target vs. visual size] The 24px-tall track needs invisible vertical padding to reach 44px → ensure the padding lands on the switch button, not the disclosure, so the two targets don't overlap confusingly.
- [Disclosure discoverability] Users may not notice the chevron → only show it when content is actually truncated, and rotate it on expand for a clear affordance.

## Migration Plan

Pure frontend change, no data migration. Deploy via the normal frontend PR → merge → release path. Rollback is a revert of the frontend PR. Regenerate visual baselines as part of merge. Verify locally at 412px (the reproduced defect width) that the track stays 44px and the thumb is contained, and that the guest hero renders for unauthenticated users.

## Open Questions

### Resolved

- **O1 (resolved)**: Keep the guest-hero CTA styles **settings-scoped for this change** (already shipped in v1.5.0), and extract a **shared brand primary-button primitive as a separate follow-up**. Rationale: there are now two near-identical filled primaries — `consent-btn-primary` (consent-route) and `settings-guest-hero-primary` (settings-route), both white-on-brand, brand-secondary hover, `--radius-button`, `--shadow-button`. That duplication justifies consolidation, but extracting now would pull consent-route into this change's diff and broaden blast radius for no user-facing gain. Recommended target: a CUBE **utility-layer** class (e.g. `.button-primary` / `.button-ghost`) that both routes adopt, or a small `<brand-button>` custom element if behaviour (loading/disabled states) is later needed. Tracked as a follow-up; not blocking.
- **O2 (resolved)**: The shipped copy passed `brand-vocabulary` lint (`make check` green), so no vocabulary adjustment was required.
- **O3 (resolved)**: The onboarding consent screen (`onboarding.consent.marketing`, owned by the in-flight `introduce-analytics-tool` change) still labels the marketing toggle by **geography** ("海外での分析処理を許可する"), which has drifted from the `analytics-consent` spec (two **purpose** toggles: product analytics + marketing measurement). Decision: align the onboarding marketing **toggle label/description** to the same purpose-based wording as Settings, leaving the screen's cross-border legal disclosure in the `intro`/`commitment` paragraphs untouched. This is spec-alignment, not a reinterpretation. Coordinated into `introduce-analytics-tool` so its owner keeps the aligned wording rather than reverting.
