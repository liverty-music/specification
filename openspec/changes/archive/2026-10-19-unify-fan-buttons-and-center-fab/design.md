## Context

See proposal.md (Why). The current state that shapes the approach:

- **Snack bar offset.** `shared/ui/snack-bar/snack-bar.css` adds `--bottom-banner-clearance`, which `src/styles/global.css` sets per banner with `:root:has(.signup-banner)` (8.5rem) and `:root:has(pwa-install-banner)` (4.5rem). `<pwa-install-banner>` is in the DOM for every authenticated fan, even after its inner `<aside>` is removed, so the 4.5rem applies almost always. Both banners already publish their rendered height as `--bottom-banner-height` through a `ResizeObserver` (`pwa-install-banner.ts:44`, `signup-prompt-banner.ts:18`). The FAB uses that value.
- **Buttons.** There is no shared button in the fan app. Templates use 44 page-specific classes (`checkout-btn-primary`, `event-btn-secondary`, `discover-cta` in `utilities.css`, …). Most use `--radius-button` (12px). Primary buttons fill with `--color-brand-primary`; secondary buttons are transparent with `--color-border-subtle`. The organizer has its own `console-button` custom element in a shadow root, which is out of scope.
- **CSS lint.** The project's CUBE plugin (`stylelint.config.js`) requires every block-layer rule to sit inside `@scope` (`cube/block-require-scope`), requires `[data-*]` selectors in the exception layer (`cube/exception-data-attr`), and prefers `color-mix()` for translucency (`cube/prefer-color-mix`).
- **FAB.** `src/components/fab-menu/` renders a `popover="manual"` toggle and a `popover="auto"` `<dialog role="group">` panel. The app shell mounts it with `if.bind="showNav && fabMenu.actions.length"`. Only the dashboard, discovery and my-artists routes register actions. Handedness lives in `FabMenuService.handed` and is persisted by `fab-preference-storage.ts`.
- **Open-state bug.** `detaching()` calls `panel.hidePopover()`. The `toggle` event is dispatched asynchronously, after the `toggle.trigger` binding is gone, and `if.bind` reuses the cached view model. As a result, `isOpen` stays `true` and the glyph comes back rotated.
- **Tabs.** Tabs come from the router navigation model (`nav: true` routes in `src/app-shell.ts`). Settings is one of them.

## Goals / Non-Goals

**Goals:**
- One measured value decides how far every bottom-anchored transient surface rises above a banner.
- One button style that templates opt into with markup only, linted by the existing CUBE rules.
- The FAB, the notch, the arc and the sink are pure CSS reacting to state that already exists. The only exceptions are `isOpen` and the item count/index bindings.

**Non-Goals:**
- Icon-only buttons and the organizer console's buttons.
- Changing which actions each route contributes.
- Redesigning the snack bar's severity colours or timing.

## Decisions

### D1. Snack bar offset uses the measured banner height

`snack-bar.css` replaces `var(--bottom-banner-clearance, 0px)` with `var(--bottom-banner-height, 0px)`, and the two `:root:has()` rules in `global.css` are deleted. A hidden banner publishes 0px (its host has no height), and an unmounted banner removes the property.
*Found during apply:* both banner hosts can be mounted at once (a signed-in fan's dashboard and My Artists mount the hidden signup prompt next to the install banner), and the hidden one wrote 0px over the visible one's height. Each banner now writes the variable only while it shows, and removes it only if it wrote it last.
*Alternative:* fix only the selector (`:root:has(.pwa-banner)`). Rejected: it keeps two hard-coded heights that drift from the real banner, and two mechanisms for the same job.

### D2. The button is a scoped CSS block with variants in the exception layer

A new `src/styles/button.css`, imported from `main.css`:

```css
@layer block {
  @scope (.button) {
    :scope { /* filled: shape, padding, brand-primary fill, white text, --shadow-button */ }
  }
}
@layer exception {
  .button[data-variant="outlined"]     { /* transparent, --color-border-subtle border */ }
  .button[data-variant="danger"]       { /* --color-danger fill */ }
  .button[data-variant="on-container"] { /* color-mix(in oklch, white 18%, transparent) fill, 1.5px color-mix white 62% border */ }
}
```

The markup is `class="[ button ] [ pressable ]" data-variant="outlined"`. The press shape morph and state layer come from the existing `.pressable` utility. The pending state reuses the existing `busy-on-click` attribute.
*Alternative:* a `<lm-button>` custom element like the organizer's `console-button`. Rejected: the fan app styles both `<a>` and `<button>`, needs no DI or slots, and a custom element would add a host box that changes layout in flex rows. Plain CSS has fewer concepts.
*Label size (decided during apply):* white on brand-primary measures 3.66:1, below WCAG AA's 4.5:1 for body text, and the catalog story's axe check fails on it. The fill stays brand-primary, and every variant's label is WCAG large text instead (Outfit, at least 19px, weight 700), whose minimum is 3:1. The user chose this over a darker fill (oklch 55%, 4.72:1) after comparing both. The border is 2px, not 1.5px: Chromium rounds a 1.5px border down to 1px at a device pixel ratio of 1.
*Alternative:* keep a `text` variant. Rejected: the user observed that text buttons do not read as buttons. Dismissive actions become `outlined`.

### D3. Migration maps classes by role, not by name

Each of the 44 classes moves to `[ button ]` with this mapping:
- `*-primary`, `*-cta` and `*-btn` that fill with brand-primary → no variant (filled).
- `*-secondary`, `*-ghost` and `*-text` → `outlined`.
- `*-danger` → `danger`.
- Buttons inside `snack-bar`, `signup-prompt-banner` and `pwa-install-banner` → `on-container`.

A page keeps a block class only for layout that the button does not own, such as `inline-size: 100%` inside a sheet. `discover-cta` is removed from `utilities.css`. Work goes route by route, so a regression can be traced to one route.

### D4. The update action: on-container style, a per-snack icon, a 3-iteration glow

`SnackOptions` gains an optional `icon` (an svg-icon name), which overrides the severity icon. `main.ts` passes `rotate-ccw` (an icon that already exists) for the update snack. The action button gets `[ button ]` with `data-variant="on-container"`. The update snack also sets `data-attention` on the action, which runs a `box-shadow` glow with `animation-iteration-count: 3`. The glow is disabled under reduced motion.
*Alternative:* a dedicated update-snack component. Rejected: the snack bar already supports actions, and only the icon and the attention flag differ.

*Changed after the production check:* on a phone the update snack's message wrapped beside the large shared button. The user chose, from rendered options, a compact action and a shorter message, and asked to drop the leading icon. `button.css` exposes size hooks (`--button-min-size`, `--button-padding-block`, `--button-padding-inline`, `--button-font-size`) that `snack-bar.css` sets on `.snack-action-btn` (36px tall, `step--1` label; radius and weight unchanged). The organizer console, which has no shared button, ignores them. `SnackOptions.icon: null` means no leading icon, and `main.ts` passes it for the update snack. The ja copy becomes 「新しいバージョンがあります」. Other snacks keep their severity icon. **Known AA gap, left to `snack-text-contrast`:** the compact label is no longer WCAG large text, so it needs 4.5:1, and it does not reach it. White on the on-container fill measures 3.35:1 at the brand-primary end of the info gradient and 3.06:1 at the brand-secondary end. The snack's white message already fell short before this change: 3.66 to 3.88:1 on the info gradient and 4.03:1 at the light end of the warning gradient. The user chose to keep the compact action and to darken the info and warning containers in a follow-up change (`snack-text-contrast`), after comparing that against a neutral surface and against large text in Storybook.

### D5. Four tabs and a fixed centre slot

Settings gets `nav: false`. `bottom-nav-bar` lays out a five-column grid (`1fr 1fr var(--fab-slot) 1fr 1fr`, with `--fab-slot: calc(var(--fab-size) + 2 * var(--fab-notch-gap))`). The third tab starts at column 4 (`.nav-tab:nth-child(3) { grid-column-start: 4; }`), so tabs 3 and 4 sit after the slot. The bar binds `data-notch.bind="fabMenu.actions.length > 0"`, the same condition that mounts the FAB. In the exception layer, `.nav-bar[data-notch="true"]` applies `mask: radial-gradient(circle var(--fab-notch-radius) at 50% 0, transparent 98%, #000)`, which also cuts the gradient top line. The slot stays whether or not the FAB is shown, per the user's decision.

### D6. Settings gear in the shell-hosted header

`app-shell` already knows the displayed route. It passes `show-settings.bind="isTabRoute"` to `<page-header>`, where `isTabRoute` means that the displayed route's config has `nav: true`. `page-header` renders an `<a href="settings">` with `svg-icon name="settings"` after its `<au-slot>`. Its accessible name is `nav.settings`.
*Alternative:* each tab route authors its own gear. Rejected: the page-header spec forbids routes from authoring header content for the title, and four copies would drift.

### D7. FAB geometry and the action arc

- **Tokens** (`tokens.css`): `--fab-size: 3.5rem`, `--fab-notch-gap: 0.5rem` (8px ≥ the spec's 6px), `--fab-notch-radius: calc(var(--fab-size) / 2 + var(--fab-notch-gap))`, `--fab-icon-size: 2rem`, `--fab-sunk-size: 2.5rem`.
- **Toggle position:** `inset-inline-start: 50%`, `translate: -50% 0`, and `inset-block-end: calc(var(--bottom-nav-height) + env(safe-area-inset-bottom) + var(--bottom-banner-height, 0px) - var(--fab-size) / 2)`.
- **Arc:** the panel stays a `popover="auto"` `<dialog role="group">` (the accessibility contract is unchanged). It is positioned at the FAB centre with zero size and `overflow: visible`. Each item is absolutely placed with CSS `offset-path: path(...)`, `offset-rotate: 0deg` and `offset-anchor: center`, at `offset-distance: calc((var(--i) + 1) / var(--n) * 92%)`. `--i` and `--n` are bound per item from the repeat (`$index`, `actions.length`).
  - The right-handed path is a tall curve from the FAB centre that rises about 190px and reaches about 130px to the right (`M0 0 C 5 -82, 60 -152, 155 -192`, tuned so that four 48px items keep 56px or more of vertical separation). Left-handed mode uses the mirrored path through `[data-handed="left"]`.
  - Labels sit on the outer side: to the left of the icon when right-handed, to the right when left-handed.
- **Motion:** open animates `offset-distance` from 0 to the item's distance with the spatial spring, staggered by `--i`. Under reduced motion the duration is near-instant (the existing `--_duration-reduced` convention).
- **Margins:** the 16px screen margin is checked at a 320px viewport in the e2e test (D10). If four items do not fit, the path is scaled with `min()` against `100vi`.

*Changed during apply:*
- The path above keeps only 31 to 52px of vertical separation and reaches 136px right of the FAB, past the 16px margin at 320px. A numeric search over Bézier control points chose `M0 0 C 0 -100, 70 -140, 110 -260`: four items 56px or more apart vertically, the last 102px right of the FAB (34px margin at 320px). No `min()` scaling is needed.
- Up to four items take fixed steps along the path (`(i + 1) / max(n, 4) * 92%`), so one or two actions sit near the FAB instead of at the top of the arc; five or more share it evenly.
- The item surface (`--md-color-menu-surface`) is lightened from oklch 30% to 50%, so items reach the WCAG 1.4.11 3:1 against the page dimmed by the scrim, and white labels stay above 4.5:1.
- Routes order their actions closest-first for the arc: the dashboard contributes beam, filter, mode switch, help; My Artists edit, help.
- **Bottom banners (stopgap).** D7 put the FAB's centre on the top edge of a visible banner, where it covers the banner's text and leaves an empty notch. While the signup prompt or the install banner is visible on a route with actions, `global.css` sets `--fab-floating: 1`: the FAB floats one `space-s` step above the banner at full size and does not sink, the bar closes the notch (zero mask radius), and the snack bar sits one `space-s` step above the FAB. The user chose this over keeping the FAB in the notch (it would cover the banner's bottom) after comparing both. Replacing the two banners with snack bars, which would remove this exception and the banner height variable, is left to a separate change: a persistent snack would keep the FAB sunk for most fans, which needs its own decision.
*Alternative:* trigonometric `translate` per item (`cos()` and `sin()`), as in the earlier mock. Rejected: it produces a circular arc around the FAB, which is the opposite curvature of the thumb sweep. A Bézier path describes the tall thumb arc directly.

*Changed after the production check:* a popover's `::backdrop` does not catch taps, so a tap outside the open arc closed it and also reached the page (a tab navigated, an event card opened its sheet). The scrim is now a `.fab-scrim` element inside the panel, fixed over the viewport, whose click closes the arc. When the arc opens, the FAB popover is hidden and shown again, so it re-enters the top layer above the panel and stays the visible close control.

### D8. Sink while a snack bar is open: a root flag, not a service

`global.css` adds `:root:has(.snack-item:popover-open) { --fab-sunk: 1; }`. `fab-menu.css` derives `scale` and `translate` from `var(--fab-sunk, 0)`, so the 56px FAB becomes 40px and lies entirely inside the bar's height. The notch stays cut while the FAB is sunk, so the FAB reads as resting in its socket. The bar needs no extra state.
*Alternative:* the snack bar publishes an open count through a DI service that fab-menu observes. Rejected: it couples two independent surfaces for a purely visual reaction. The root flag follows the pattern already used for banners. A rule inside `@scope (fab-menu)` cannot match `:root`, which is why the flag is a custom property set from the global layer.

### D9. Glyph: an inline SVG owned by fab-menu

The equalizer and the `×` are two inline SVGs in `fab-menu.html`, sized by `--fab-icon-size`. They cross-fade and rotate on `data-open`. The bars carry a one-shot `scaleY` keyframe that runs only when `data-open` turns true. They are not `svg-icon`s, because the morph animates individual bars, and the `svg-icon` sizes (`lg` 1.5rem, `xl` 2.5rem) do not include 2rem.

### D10. Bug fix and tests

- `FabMenu.detaching()` sets `this.isOpen = false` before hiding the popovers. A unit test in `fab-menu.spec.ts` asserts that `isOpen` is false after detach and reattach.
- Every ADDED or MODIFIED scenario gets an `@spec` annotation:
  - **Storybook (component tests):** the button catalog (`src/styles/button.stories.ts`, with `toMatchScreenshot` like `svg-icon.stories.ts`), the snack-bar update action (border, glow count, icon), and the page-header gear.
  - **Playwright functional e2e:** snack placement with and without a banner, the FAB centre and notch, the arc layout (no overlap and 16px margins at 320px and 390px), the sink, the collapsed state after navigation, the Discovery top layer (`elementFromPoint` at the FAB centre), left-handed mirroring, four tabs and the flat bar on Tickets, and the Settings label.
  - The existing `fab-menu-beam-toggle.spec.ts` "Toggle button placement and icon" stays valid, because the item keeps its icon and label.

## Risks / Trade-offs

- [Visual regressions while migrating 44 classes] → migrate route by route, run `rendered-screens.spec.ts` (styles and axe) on each route, and check each route by eye in Storybook or the prod build before merging.
- [Moving Settings out of the tab bar breaks fans' habit] → the gear sits at the same trailing header position on all four tab pages. The product has two users today.
- [`offset-path` with `path()` support] → it is Baseline in Chrome 116+, Safari 16+ and Firefox 72+, which covers the PWA's target browsers. A browser without support places items at the FAB centre. The e2e test runs on Chromium and WebKit.
- [Four arc items on a 320px screen] → the D7 margin check at 320px, plus `min()` scaling of the path.
- [Notch mask and the gradient top line] → masking the whole bar element (including `::before`) keeps one shape. It is verified in the bottom-nav Storybook screenshot.

## Migration Plan

One frontend PR (the user chose one change). Rollback is a revert of that PR. No data migration is needed: the handedness preference keeps its storage key and values. Production verification after deploy: open the dashboard on a phone, trigger the update snack bar (deploy a second build), and confirm the placement, the sink and the arc.
