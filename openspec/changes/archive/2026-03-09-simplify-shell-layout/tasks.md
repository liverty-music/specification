## 1. Shell layout restructure

- [x] 1.1 Update `my-app.html`: wrap `au-viewport` in `<main display="contents">` for semantic landmark, remove `<main>` as a layout box. Move overlay components outside `au-viewport` as direct children of `my-app`.
- [x] 1.2 Update `my-app.css`: change `au-viewport` from `display: block; height: 100%` to `display: grid` so route components auto-stretch. Remove any `overflow` rules from `au-viewport`.
- [x] 1.3 Verify `<main display="contents">` passes through grid without creating a layout box (test that `au-viewport` still occupies the `1fr` track correctly).

## 2. Discover page class rename

- [x] 2.1 Rename `.container` to `.discover-layout` in `discover-page.css` (all selectors using `.container`).
- [x] 2.2 Update `discover-page.html` to use `discover-layout` class instead of `container`.
- [x] 2.3 Remove the `width: 100%` workaround from `.bubble-area` in `discover-page.css` (no longer needed once `.container` collision is resolved).

## 3. Route scroll ownership

- [x] 3.1 Verify `settings-page.html` has its own `overflow-y: auto` on the scrollable container (already has `h-full overflow-y-auto`).
- [x] 3.2 Audit all other route components: remove any `height: 100%` declarations that were part of the relay chain, confirm routes that need scrolling have their own `overflow-y: auto`.
- [x] 3.3 Verify discover page does NOT scroll at the route level (canvas fills viewport, only search results scroll independently).

## 4. Overlay independence

- [x] 4.1 Verify overlay components (`pwa-install-prompt`, `notification-prompt`, `error-banner`) render correctly in the top layer regardless of their DOM position within `my-app`.
- [x] 4.2 Confirm overlays do not create implicit grid rows in the `my-app` grid.

## 5. Visual verification

- [x] 5.1 Verify discover page: bubbles render at correct size, canvas fills the bubble-area, search mode works.
- [x] 5.2 Verify settings page: content scrolls vertically, fills available height. (Moved to `add-layout-assertions` as authenticated layout test)
- [x] 5.3 Verify dashboard page: layout correct with bottom nav visible. (Covered by `dashboard.layout.spec.ts` concert card rendering tests)
- [x] 5.4 Verify onboarding flow: full-height layout with no bottom nav.
- [x] 5.5 Run `make check` (lint + test) to ensure no regressions.
