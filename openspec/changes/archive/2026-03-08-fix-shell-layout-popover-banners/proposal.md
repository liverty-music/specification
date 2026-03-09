## Why

PR #133 replaced the fixed-position bottom nav with a CSS Grid app shell (`grid-rows-[auto_auto_1fr]`), but the two promotional banners (PWA install prompt, notification prompt) remain as in-flow Grid children. When `notification-prompt` is removed from the DOM by `if.bind`, the Grid has only 2 children for 3 row definitions, causing `au-viewport` to land on the `auto` row instead of the `1fr` row. The viewport collapses to content height (177 px), the discover page canvas receives a 0 px bubble area, and all artist bubbles are invisible.

Secondary issue: `<discover-page>` is rendered as `display: inline` (Aurelia 2 CE default), so even with a correct parent height, `height: 100%` on its `.container` cannot propagate through an inline element.

Root cause: promotional banners are ephemeral notifications that should never participate in structural layout. They belong in the top layer (Popover API), not in Grid track definitions.

## What Changes

1. **Move PwaInstallPrompt to `popover="manual"`** — Remove it from the `<main>` Grid. Position as a fixed top banner in the top layer. Show/hide via `showPopover()` / `hidePopover()` instead of relying on in-flow `show.bind`.

2. **Move NotificationPrompt to `popover="manual"`** — Same treatment. Remove from Grid, promote to top layer.

3. **Simplify `<main>` Grid** — With banners removed, `<main>` no longer needs `grid-rows-[auto_auto_1fr]`. It becomes a simple block container holding only `<au-viewport>` with `overflow-y: auto`.

4. **Move banner elements outside `<main>`** — Place them as siblings of `<main>` (or after `<bottom-nav-bar>`) since they are top-layer elements and their DOM position is irrelevant to rendering.

5. **Fix `<discover-page>` host styling** — Add `:host { display: block; height: 100%; }` to ensure height propagation from `au-viewport` through the custom element host to its `.container`.

6. **Fix MyArtists undo toast layering** — Convert the inline `position: absolute` undo toast to `popover="manual"` so it renders above `<dialog>` elements (passion selector, context menu) when both are visible.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `app-shell-layout`: The `<main>` element is no longer a CSS Grid. It is a block container with `overflow-y: auto` and `height` inherited from the outer Grid `1fr` track. Promotional banners are no longer structural children.
- `frontend-pwa-install-prompt`: PwaInstallPrompt uses `popover="manual"` + `position: fixed` for top-layer rendering. Zero layout shift on show/hide.
- `frontend-notification-prompt`: NotificationPrompt uses `popover="manual"` + `position: fixed` for top-layer rendering. Zero layout shift on show/hide.
- `frontend-artist-discovery`: The discover page canvas now receives the full available height, fixing the invisible bubble bug.

## Impact

- **Frontend repo only** — no backend or specification changes
- **Files affected**:
  - `src/my-app.html` — Remove banners from `<main>`, simplify Grid
  - `src/my-app.css` — Update `au-viewport` height propagation rules
  - `src/components/pwa-install-prompt/pwa-install-prompt.html` — Add `popover="manual"`, change to fixed positioning
  - `src/components/pwa-install-prompt/pwa-install-prompt.ts` — Replace `show.bind` with `showPopover()` / `hidePopover()`
  - `src/components/notification-prompt/notification-prompt.html` — Add `popover="manual"`, change to fixed positioning
  - `src/components/notification-prompt/notification-prompt.ts` — Replace `show.bind` with `showPopover()` / `hidePopover()`
  - `src/routes/discover/discover-page.ts` — Add `:host` styles for height propagation
  - `src/routes/my-artists/my-artists-page.html` — Convert undo toast to `popover="manual"`
  - `src/routes/my-artists/my-artists-page.ts` — Add `showPopover()` / `hidePopover()` calls for undo toast
- **No breaking API changes** — purely presentational and layering fixes
- **Blocks**: This is a bug fix — discover page bubbles are completely invisible in production
