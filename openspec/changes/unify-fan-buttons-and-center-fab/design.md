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

*Alternative:* trigonometric `translate` per item (`cos()` and `sin()`), as in the earlier mock. Rejected: it produces a circular arc around the FAB, which is the opposite curvature of the thumb sweep. A Bézier path describes the tall thumb arc directly.

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
