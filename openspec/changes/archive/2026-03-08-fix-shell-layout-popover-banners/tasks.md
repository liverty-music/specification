## 1. Simplify App Shell Layout

- [x] 1.1 In `my-app.html`: remove `grid grid-rows-[auto_auto_1fr] overflow-hidden` from `<main>`, replace with block layout (`overflow-y-auto`)
- [x] 1.2 In `my-app.html`: move `<pwa-install-prompt>` and `<notification-prompt>` outside `<main>` (as siblings after `<bottom-nav-bar>`)
- [x] 1.3 In `my-app.css`: ensure `au-viewport` has `display: block; height: 100%;` for height propagation

## 2. PwaInstallPrompt → popover="manual"

- [x] 2.1 In `pwa-install-prompt.html`: add `popover="manual"` to root element, change positioning to `fixed` top banner with logical inset properties
- [x] 2.2 In `pwa-install-prompt.ts`: replace visibility via `show.bind` with `showPopover()` / `hidePopover()` calls; add element ref for the popover container
- [x] 2.3 Override UA popover `margin: auto` centering with explicit `margin: 0` and top positioning

## 3. NotificationPrompt → popover="manual"

- [x] 3.1 In `notification-prompt.html`: add `popover="manual"` to root element, change positioning to `fixed` top banner with logical inset properties
- [x] 3.2 In `notification-prompt.ts`: replace visibility via `show.bind` with `showPopover()` / `hidePopover()` calls; add element ref for the popover container

## 4. Fix Discover Page Height Propagation

- [x] 4.1 In `discover-page.ts`: add `:host { display: block; height: 100%; }` to `shadowCSS` or `static dependencies`

## 5. MyArtists Undo Toast → popover="manual"

- [x] 5.1 In `my-artists-page.html`: change undo toast from `if.bind` + `position: absolute` to persistent DOM with `popover="manual"` attribute
- [x] 5.2 In `my-artists-page.ts`: call `showPopover()` when `undoVisible` becomes true, `hidePopover()` when false

## 6. Verification

- [x] 6.1 Run `make check` (lint + test) and fix any failures
- [x] 6.2 Verify discover page bubbles render correctly (Playwright or manual on dev.liverty-music.app)
- [x] 6.3 Verify PWA install banner appears/disappears without layout shift
- [x] 6.4 Verify notification banner appears/disappears without layout shift
- [x] 6.5 Verify undo toast is visible even when a dialog is open in MyArtists page
- [x] 6.6 Verify all other routes (dashboard, tickets, settings) still render correctly with the simplified `<main>`
