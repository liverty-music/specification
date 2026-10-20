## Context

See proposal.md for the motivation. The code this change touches:

- **FAB flags.** `src/styles/global.css` sets `--fab-sunk: 1` from `:root:has(.snack-item:popover-open)` and `--fab-floating: 1` from `:root:has(:is(.signup-banner, .pwa-banner)):has(fab-menu .fab-toggle)`. `fab-menu.css` derives the FAB's centre and scale from both. `bottom-nav-bar.css` closes the notch with `--fab-floating`, and `snack-bar.css` adds the floating FAB's size to the snack's offset.
- **Banner height.** Both banners publish their rendered height on `:root` as `--bottom-banner-height` from a `ResizeObserver`, and only while they show. The FAB and the snack bar read it. The route area does not, which is frontend#787.
- **Route area.** `app-shell.css` places `<au-viewport>` in a `minmax(0, 1fr)` grid row above the navigation row. Routes size themselves with `block-size: 100%` and scroll inside (`.settings-scroll` and the same pattern in my-artists, tickets, dashboard and discovery).
- **Banners.** The install banner (`src/components/pwa-install-banner/`) lives in the app shell and stays mounted across tab changes. It has an icon, a close button that writes `pwaBanner.dismissed` to `sessionStorage`, and a single-line label that ellipsises. The signup prompt (`src/components/signup-prompt-banner/`) is hosted by the dashboard and My Artists routes and stacks its message above its button. Both buttons use `data-variant="on-container"` and glow three times when the banner appears.
- **Preview.** The user chose the layout, the button, the copy and the cue in the artifact "バナーの注目演出 3 案" (option 3, a light that runs along the line and across the CTA).

## Goals / Non-Goals

**Goals:**
- One rule for the FAB under any bottom surface, and the route area ending above a banner, so nothing on the screen is covered.
- Both banners in one row that fits on one line at every phone width, with a filled CTA and a recurring cue that never moves the CTA.

**Non-Goals:**
- Turning the banners into snack bars, or changing when each banner shows (onboarding, authentication, post-signup suppression).
- The notification prompt, apart from removing the two install-banner scenarios from its spec.

## Decisions

### D1. A visible banner sinks the FAB, through the existing flag

`global.css` sets `--fab-sunk: 1` from `:root:has(.snack-item:popover-open, .signup-banner, .pwa-banner)`. The `--fab-floating` rule and every use of it go: the `--_floating` term in `fab-menu.css` (the FAB's centre and the sunk factor), the notch-closing factor in `bottom-nav-bar.css` (the notch now stays cut, as it already does while sunk under a snack), and the floating FAB's term in the snack bar's `--_inset-end`. The snack still adds `--bottom-banner-height`, so it sits above a visible banner.

*Alternative:* keep the floating FAB and only reserve space for it. Rejected: the user chose to treat a banner like a snack bar, and one flag for both is fewer concepts than two.

### D2. The route area ends above a visible banner, with one rule

`app-shell.css` gives `au-viewport` `padding-block-end: var(--bottom-banner-height, 0px)` with `box-sizing: border-box`. The banners publish that height only while they show, so the row is unchanged without a banner. Routes keep `block-size: 100%`, which now resolves against the shorter content box: every scroll area ends at the banner's top edge, and an empty state centres in the area above it. This follows "Pages do not compensate for navigation bar height": the shell compensates, not the routes.

*Alternative:* pad each route's scroll container, as frontend#787 suggested. Rejected: five routes, and an empty state would still centre over the banner.

### D3. One row, one text size from the banner's width

Each banner is `container-type: inline-size` with a grid of `minmax(0, 1fr) auto`. A block-private property `--_banner-text: clamp(12px, 4.4cqi, 16px)` sets the message's `font-size` and the button's `--button-font-size`. 4.4cqi keeps the longest message (14 characters) and the button on one line at 320px; the bound comes from the message width plus the button's padding and label against the banner's content box at 320px, with about 5% to spare. The message has `white-space: nowrap` and no `text-overflow`, so a copy that no longer fits shows as clipped text that the E2E check in D7 catches, rather than as an ellipsis. The icon, the close button and the right padding that reserved its space are removed.

*Alternative:* fixed `--step--1` for both. Rejected after the preview: `--step--1` follows the viewport, not the banner, and clipped the message.

### D4. The filled button takes the primary role pair, at a tone where white passes

The banner CTAs drop `data-variant="on-container"` and take the default (filled) variant, with the compact hooks the snack bar's action uses: `--button-min-size: 2.25rem`, `--button-padding-block: var(--space-3xs)`, `--button-padding-inline: var(--space-s)` and `--button-font-size: var(--_banner-text)`.

A compact label (12 to 16px bold) is not WCAG large text, so it needs 4.5:1. White on brand-primary (oklch 65% 0.28 350) is 3.67:1 and can reach 4.5:1 only at a lightness of about 57.5% or below. Rather than darken the fill inside the banners, the fix goes into the role tokens, which the design-tokens spec already requires components to use ("Color roles with guaranteed on-color pairing"):

- `tokens.css`: `--md-color-primary: oklch(from var(--color-brand-primary) 57% c h)` (brand hue and full chroma, the highest tone at which white passes, 4.64:1) and `--md-color-on-primary: var(--color-white)`. `--color-brand-primary` stays at 65% for the FAB, gradients, lines and glows.
- `button.css`: the filled variant's `background` and `color` become `--md-color-primary` / `--md-color-on-primary` instead of `--color-brand-primary` / `--color-white`, so every filled button passes at every size, and the large-text comment goes.
- The two other places that put text on a primary fill pair the physical `--color-brand-primary` with the dark `--md-color-on-primary`: the selected date tab (`event-date-tabs.css`) and the followed state of the event page's follow button (`event-route.css`). Both move to the role pair; with `on-primary` now white they would otherwise fall to 3.67:1.
- `circular-progress.css` colours the spinner with `--md-color-primary`; at 57% it measures 4.06:1 against the base surface, above the 3:1 a non-text indicator needs.

The user compared this (option C) with the M3 pairs already in the tokens (primary with a dark label, and primary-container with a near-white label) and chose it: it keeps the brand's vivid pink and the white label of every other filled button.

*Alternative:* darken the fill only in the banners (`oklch(from … 57% c h)` in the banner CSS). Rejected by the user: a value picked per component bypasses the token layer that keeps the app consistent.
*Alternative:* `primary` with the existing dark `on-primary` (5.21:1), or `primary-container` with `on-primary-container` (6.25:1). Rejected by the user after the preview "filled ボタンの色の役割".

### D5. The attention cue is one CSS animation with a count

A `::before` on the banner's top line and an `::after` on the CTA run one keyframe each, `banner-cue 12s ease-in-out 5`: the light crosses the line in the first ~9% of the cycle and the CTA in ~8–14%, and both rest for the remaining ~10 seconds. The count of 5 ends the cue after about a minute, which also meets WCAG 2.2.2 now that neither banner can be closed. Both sit inside `prefers-reduced-motion: no-preference`. The `::before`/`::after` only paint (`transform` on an absolutely placed, `overflow: hidden` layer), so the banner and the CTA keep their box.

The signup prompt is mounted by each route, so its cue restarts per route by itself. The install banner stays mounted in the app shell, so it restarts its cue after each completed navigation: it subscribes to the router's navigation-end event in `attached()`, sets `currentTime = 0` on its own cue animations, and disposes the subscription in `detaching()`.

*Alternative:* a JavaScript timer that toggles a class. Rejected: a counted CSS animation needs no timer to clean up, and only the install banner's restart needs a subscription.

### D6. The dismiss goes

`pwa-install-banner` loses `dismissed`, `dismiss()`, the close button and its `pwaInstallBanner.close` keys, and `SessionKeys.pwaBannerDismissed` is deleted. `isVisible` becomes `pwaInstall.shouldShowInstallBanner`.

### D7. Copy and keys

`pwaInstallBanner.label` becomes 「新着ライブ通知を受け取ろう！」 / "Get new show alerts!". `myArtists.signupBanner.message` becomes 「フォロー履歴を保存しよう！」 / "Save your follows!". The signup button moves from `common.createAccount`, which only this button reads, to a new `signupBanner.cta` ("Sign Up" in both locales), and `common.createAccount` is deleted. The English copy is the user's proposal accepted in exploration.

### D8. Tests

- **Stories** (`signup-prompt-banner.stories.ts`, `pwa-install-banner.stories.ts`, `.storybook/bottom-banner.ts`): the surface, the one row with no icon or close, the filled compact button (fill, 36px height, label size equal to the message's, 4.5:1), the message text, the cue (`animationIterationCount` 5, `animationDuration` 12s, the CTA's box unchanged while it runs), reduced motion, and the entrance.
- **E2E** (`e2e/functional/`): the fit at 320, 360, 375 and 412px in `ja` and `en` (`scrollWidth <= clientWidth` for the message and the button), the FAB sunk under a visible banner and returning when it goes, the notch kept, the snack's placement with a banner, the Settings Sign out row and the My Artists empty-state button hit-testable with a banner shown, and the install banner's cue restarting after a tab change.

### D9. The snack bar's severity colours become tokens

`snack-text-contrast` set the snack's gradient stops inside `snack-bar.css` (info `oklch(from brand-primary 50.5% c h)` and `oklch(from brand-secondary 48% c h)`, warning `oklch(47.5% 0.16 75deg)`, error `oklch(40% 0.2 25deg)` and `oklch(45% 0.18 25deg)`). These move to `tokens.css` as `--md-color-snack-info-from`, `--md-color-snack-info-to`, `--md-color-snack-warning`, `--md-color-snack-error-from` and `--md-color-snack-error-to`, each documented with the white label and the on-container action it carries at 4.5:1, and `snack-bar.css` reads them. The values and the rendered snack do not change, so the snack's stories and screenshot stay as they are. The organizer console still restyles the container through `--snack-bar-container`.

*Alternative:* derive the info stops from `--md-color-primary`. Rejected: the action needs 50.5% mid-gradient (see `snack-text-contrast`), darker than the button role.

## Risks / Trade-offs

- **[The FAB stays small for as long as a banner shows]** The install banner shows to every signed-in fan until the app is installed. → The sunk FAB stays tappable (an existing scenario), and the user chose this over the floating FAB.
- **[The banner can no longer be closed]** A fan who will not install keeps seeing it. → Intended by the user; the guide sheet's 「追加しました」 removes it, and the cue stops after five plays per route.
- **[The Discovery canvas loses the banner's height while the install banner shows]** → Bubbles then never sit under the banner. The canvas already sizes from its container.
- **[Every filled button in the app turns a shade deeper]** 65% to 57% lightness at the same hue and chroma. → The user chose it in the preview; the button catalog's screenshot is regenerated and reviewed.
- **[The selected date tab and the followed button change from a dark label to a white one]** → They now follow the same role pair as the filled button.
