## 1. `isolation: isolate` for component-internal stacking

### 1a. discover-page.css
- [x] Add `isolation: isolate` to `.container`
- [x] Remove `z-index` from `.container::before` (0), `.search-bar` (20), `.genre-chips` (15), `.orb-label` (15), `.search-results` (10), `.onboarding-hud` (20), `.complete-button-wrapper` (20)
- [x] Verify DOM source order produces correct layering: starfield `::before` < canvas < search bar < genre chips < onboarding HUD < complete button

### 1b. loading-sequence.css
- [x] Add `isolation: isolate` to root wrapper element
- [x] Remove `z-index` from all 6 selectors (`.container::before` 0, `.pulsing-orb` 1, `.message-container` 1, `.step-dots` 1, `.step-label` 1, `.progress-label` 1)

### 1c. live-highway sticky date separator
- [x] Add `isolation: isolate` to the scroll container in `live-highway.html`
- [x] Remove `z-20` from the sticky date separator element

## 2. `<dialog>` + `showModal()` for modal overlays

### 2a. event-detail-sheet
- [x] Replace backdrop `<div class="fixed inset-0 z-40 ...">` and sheet `<div class="fixed inset-x-0 bottom-0 z-50 ...">` with single `<dialog ref="dialogElement">`
- [x] Add `showModal()` in `open()` and `close()` in close method
- [x] Style `::backdrop` with `background: oklch(0% 0 0 / 0.6); backdrop-filter: blur(4px)`
- [x] Add `@starting-style` slide-up animation (translateY 100% to 0, 300ms ease-out)
- [x] Click-outside-to-close via `event.target === dialogElement`
- [x] Preserve swipe-to-dismiss touch handlers on `<dialog>` content area
- [x] Suppress `cancel` event when `isDismissBlocked` (onboarding DETAIL step)
- [x] Remove `z-40`, `z-50` classes and `if.bind="isOpen"` from backdrop

### 2b. my-artists-page context menu
- [x] Replace `<div class="absolute inset-0 z-50 ...">` with `<dialog ref="contextMenuDialog">`
- [x] Call `showModal()` in `openContextMenu()`, `close()` in `closeContextMenu()`
- [x] Style `::backdrop`, add `@starting-style` slide-up animation
- [x] Handle backdrop click-to-close and ESC-to-close
- [x] Remove z-index classes and manual backdrop `<div>`

### 2c. my-artists-page passion selector
- [x] Replace `z-50` passion selector overlay with `<dialog>`
- [x] Add `showModal()`/`close()` lifecycle

### 2d. my-artists-page passion explanation
- [x] Replace `<div class="absolute inset-0 z-[60] ...">` with `<dialog ref="passionExplanationDialog">`
- [x] Suppress `cancel` event (non-dismissible tutorial modal)
- [x] Style `::backdrop` with `background: oklch(0% 0 0 / 0.7)` (matching `bg-black/70`)
- [x] Auto-close when tutorial step completes

### 2e. tickets-page QR modal
- [x] Replace `<div role="dialog" aria-modal="true" class="fixed inset-0 z-50 ...">` with `<dialog ref="qrDialog">`
- [x] Remove manual `role="dialog"`, `aria-modal="true"`, `tabindex="-1"`, `keydown.trigger` (native `<dialog>` provides all)
- [x] Call `showModal()` when QR data available, `close()` in `dismissQr()`
- [x] Style `::backdrop` for dark blur overlay

### 2f. tickets-page proof generation
- [x] Replace `<div role="alert" class="fixed inset-0 z-50 ...">` with `<dialog ref="generatingDialog">`
- [x] Suppress `cancel` event (non-dismissible during generation)
- [x] Retain `role="alert"` and `aria-live="polite"` on inner content
- [x] Auto-close when generation completes

### 2g. signup-modal
- [x] Replace `z-[70]` wrapper with `<dialog>`
- [x] Suppress `cancel` event (non-dismissible)
- [x] Style `::backdrop`

### 2h. error-banner
- [x] Replace `z-[100]` wrapper with `<dialog>`
- [x] Style `::backdrop`, add auto-dismiss behavior

## 3. `popover="manual"` for persistent non-modal elements

### 3a. bottom-nav-bar
- [x] Add `popover="manual"` attribute to nav container element
- [x] Call `this.navElement.showPopover()` in `attached()` lifecycle
- [x] Remove `z-30` class
- [x] Verify nav bar remains visible across route navigations
- [x] Verify `<dialog>` modals paint above nav bar (later Top Layer insertion)

### 3b. toast-notification
- [x] Add `popover="manual"` attribute to toast container
- [x] Call `showPopover()` when toast displayed, `hidePopover()` when dismissed
- [x] Remove `z-50` class
- [x] Retain `pointer-events: none` on container with `pointer-events: auto` on toast items
- [x] Verify toasts paint above dialogs and nav bar

### 3c. coach-mark overlay
- [x] Add `popover="manual"` to `.coach-mark-overlay` element
- [x] Call `showPopover()` on activation, `hidePopover()` on dismissal
- [x] Remove `z-index: 9999` from `coach-mark.css`
- [x] Verify overlay paints above all other Top Layer elements (latest insertion)
- [x] Verify click-through on spotlight area still works

## 4. CSS Anchor Positioning for coach-mark tooltip

- [x] Set `anchor-name: --coach-target` dynamically on the target element via `style.setProperty('anchor-name', ...)`
- [x] Set `position-anchor: --coach-target` on the tooltip element
- [x] Use `position-area` for placement direction (top/bottom/left/right of target)
- [x] Add `position-try-fallbacks: flip-block, flip-inline` for viewport edge handling
- [x] Remove `updatePosition()` JS method that uses `getBoundingClientRect()` for tooltip positioning
- [x] Remove `ResizeObserver` for tooltip position recalculation (CSS handles this automatically)
- [x] Keep `getBoundingClientRect()` for spotlight canvas cutout rendering (canvas cannot use CSS positioning)

## 5. Tests

- [x] Update `event-detail-sheet` tests: query `<dialog>`, verify `[open]` attribute
- [x] Update `my-artists-page` tests: verify context menu and passion dialogs
- [x] Update `tickets-page` tests: verify QR dialog and generation overlay
- [x] Add `bottom-nav-bar` test: verify `popover="manual"` attribute and visibility
- [x] Add `toast-notification` test: verify popover show/hide lifecycle
- [x] Add `coach-mark` test: verify popover activation and CSS anchor attributes
- [x] Verify swipe-to-dismiss on `event-detail-sheet` `<dialog>`
- [x] Verify dismiss-block suppresses ESC during onboarding DETAIL step

## 6. Verification

- [x] Run `make check` in frontend repo (lint + test)
- [x] `grep -rn 'z-index' frontend/src/` — expect 0 results
- [x] `grep -rn 'z-[0-9]\|z-\[' frontend/src/` — expect 0 Tailwind z-index classes
- [ ] Visual: discover page layers correctly (starfield behind, UI above canvas)
- [ ] Visual: event detail sheet slides up as `<dialog>`, backdrop dims including nav bar
- [ ] Visual: bottom nav bar visible via popover, dialogs paint above it
- [ ] Visual: toast notifications appear above dialogs
- [ ] Visual: coach-mark overlay and tooltip position correctly via Anchor Positioning
- [ ] Visual: coach-mark paints above all other elements
- [ ] Test on mobile Safari and Chrome for popover + fixed position behavior
