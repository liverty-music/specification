## 1. Toggle layout integrity (CSS)

- [x] 1.1 Add `flex-shrink: 0` to `.settings-toggle-track` in `settings-route.css` so the track never collapses below its declared `2.75rem`
- [x] 1.2 Add `min-inline-size: 0` to the toggle text column so it absorbs remaining width and wraps instead of starving the track
- [x] 1.3 Switch toggle rows to `align-items: flex-start` so the control aligns to the first line of multi-line content
- [x] 1.4 Decouple the toggle description styling from `.settings-row-hint`'s `margin-inline-start: var(--space-l)` (use a dedicated class with no inherited inline-start indent)
- [x] 1.5 Verify at 412px that the rendered track width stays 44px and the thumb is contained in both ON and OFF states with no card-edge overflow (re-run the Playwright measurement from the design doc)

## 2. Expandable toggle description (markup + a11y)

- [x] 2.1 Restructure each long-description toggle row into two sibling controls: a disclosure `<button aria-expanded>` (label + collapsible description + chevron) and the `<button role="switch" aria-checked>` (track/thumb)
- [x] 2.2 Collapse the description by default (truncate to collapsed length) and reveal full text on disclosure activation; toggle `aria-expanded` accordingly
- [x] 2.3 Render the chevron affordance only when the description exceeds the collapsed length; rotate it on expand
- [x] 2.4 Ensure the switch activation target is ≥44px in the block dimension via padding on the switch button (without overlapping the disclosure target)
- [x] 2.5 Confirm activating the disclosure never changes the switch value, and vice versa

## 3. Consent toggle copy & labeling (i18n)

- [x] 3.1 Keep section title `プライバシーと分析`; update `settings.analytics.toggleLabel`/`toggleDescription` to the analytics opt-in-friendly copy (benefit + "no PII")
- [x] 3.2 Relabel `settings.analytics.crossBorderLabel`/`crossBorderDescription` to describe ad-effectiveness measurement (purpose), not geography; keep the toggle bound to `consent.marketingMeasurement`
- [x] 3.3 Update the `en` locale mirror for all changed `settings.analytics.*` keys
- [x] 3.4 Run `make lint` brand-vocabulary check on the new copy and adjust to approved vocabulary if flagged (resolves O2)

## 4. Guest CTA hero (markup + CSS)

- [x] 4.1 Add a guest-only (`if.bind="!auth.isAuthenticated"`) hero card at the top of `.settings-scroll`, before the preferences section
- [x] 4.2 Style the hero distinctly: brand-tinted background + brand border, a filled primary `ログイン` button and a ghost/text `新規登録` action (scoped to the settings route per D5)
- [x] 4.3 Add hero copy: heading `ログインして、もっと便利に`, body `お気に入りと通知を、どの端末でもそのまま使えます`; remove/repurpose the old `settings.guestPrompt` string
- [x] 4.4 Remove the guest branch from the bottom ACCOUNT section; keep authenticated-only controls there
- [x] 4.5 Delete the orphan `.settings-guest-prompt` class (markup usage + ensure no CSS references remain)

## 5. iOS-only sound hint

- [x] 5.1 Compute an `isIOS` flag in `settings-route.ts` (platform/UA check, defaulting to false when uncertain)
- [x] 5.2 Gate the `settings.soundEffectsHint` row with `if.bind` on the iOS flag

## 6. Tests & verification

- [x] 6.1 Update/extend `test/routes/settings-route.spec.ts` for the disclosure + switch split, iOS-hint gating, and guest-hero rendering by auth state
- [x] 6.2 Regenerate `e2e/visual/settings.auth.visual.spec.ts` baselines (delete stale visual-baseline artifacts to force regen per project process)
- [x] 6.3 Update `e2e/pwa/pwa-settings.spec.ts` if selectors changed
- [x] 6.4 Run `make check` (lint + test) green locally
- [x] 6.5 Manually verify on a 412px viewport: contained toggle, expandable descriptions, guest hero for unauthenticated users, no iOS hint on non-iOS

## 7. Ship

- [x] 7.1 Open the frontend PR (Conventional Commit, body explaining why, `Refs: #<issue>`); pass CI
- [x] 7.2 Address review, merge to `main`
- [x] 7.3 Cut the frontend GitHub Release so the change reaches production; confirm the prod rollout reflects the new Settings UI
- [x] 7.4 Resolve open questions O1 (CTA primitive scope) and O3 (coordinate the marketing-toggle wording with `introduce-analytics-tool`)
