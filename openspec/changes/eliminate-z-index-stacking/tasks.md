## 1. `isolation: isolate` for component-internal stacking

### 1a. discover-page.css
- [ ] Add `isolation: isolate` to `.container`
- [ ] Remove `z-index` from `.container::before` (0), `.search-bar` (20), `.genre-chips` (15), `.orb-label` (15), `.search-results` (10), `.onboarding-hud` (20), `.complete-button-wrapper` (20)
- [ ] Verify DOM source order produces correct layering: starfield `::before` < canvas < search bar < genre chips < onboarding HUD < complete button

### 1b. loading-sequence.css
- [ ] Add `isolation: isolate` to root wrapper element
- [ ] Remove `z-index` from all 6 selectors (`.container::before` 0, `.pulsing-orb` 1, `.message-container` 1, `.step-dots` 1, `.step-label` 1, `.progress-label` 1)

### 1c. live-highway sticky date separator
- [ ] Add `isolation: isolate` to the scroll container in `live-highway.html`
- [ ] Remove `z-20` from the sticky date separator element

## 2. `<dialog>` + `showModal()` for modal overlays

### 2a. event-detail-sheet
- [ ] Replace backdrop `<div class="fixed inset-0 z-40 ...">` and sheet `<div class="fixed inset-x-0 bottom-0 z-50 ...">` with single `<dialog ref="dialogElement">`
- [ ] Add `showModal()` in `open()` and `close()` in close method
- [ ] Style `::backdrop` with `background: oklch(0% 0 0 / 0.6); backdrop-filter: blur(4px)`
- [ ] Add `@starting-style` slide-up animation (translateY 100% to 0, 300ms ease-out)
- [ ] Click-outside-to-close via `event.target === dialogElement`
- [ ] Preserve swipe-to-dismiss touch handlers on `<dialog>` content area
- [ ] Suppress `cancel` event when `isDismissBlocked` (onboarding DETAIL step)
- [ ] Remove `z-40`, `z-50` classes and `if.bind="isOpen"` from backdrop

### 2b. my-artists-page context menu
- [ ] Replace `<div class="absolute inset-0 z-50 ...">` with `<dialog ref="contextMenuDialog">`
- [ ] Call `showModal()` in `openContextMenu()`, `close()` in `closeContextMenu()`
- [ ] Style `::backdrop`, add `@starting-style` slide-up animation
- [ ] Handle backdrop click-to-close and ESC-to-close
- [ ] Remove z-index classes and manual backdrop `<div>`

### 2c. my-artists-page passion selector
- [ ] Replace `z-50` passion selector overlay with `<dialog>`
- [ ] Add `showModal()`/`close()` lifecycle

### 2d. my-artists-page passion explanation
- [ ] Replace `<div class="absolute inset-0 z-[60] ...">` with `<dialog ref="passionExplanationDialog">`
- [ ] Suppress `cancel` event (non-dismissible tutorial modal)
- [ ] Style `::backdrop` with `background: oklch(0% 0 0 / 0.7)` (matching `bg-black/70`)
- [ ] Auto-close when tutorial step completes

### 2e. tickets-page QR modal
- [ ] Replace `<div role="dialog" aria-modal="true" class="fixed inset-0 z-50 ...">` with `<dialog ref="qrDialog">`
- [ ] Remove manual `role="dialog"`, `aria-modal="true"`, `tabindex="-1"`, `keydown.trigger` (native `<dialog>` provides all)
- [ ] Call `showModal()` when QR data available, `close()` in `dismissQr()`
- [ ] Style `::backdrop` for dark blur overlay

### 2f. tickets-page proof generation
- [ ] Replace `<div role="alert" class="fixed inset-0 z-50 ...">` with `<dialog ref="generatingDialog">`
- [ ] Suppress `cancel` event (non-dismissible during generation)
- [ ] Retain `role="alert"` and `aria-live="polite"` on inner content
- [ ] Auto-close when generation completes

### 2g. signup-modal
- [ ] Replace `z-[70]` wrapper with `<dialog>`
- [ ] Suppress `cancel` event (non-dismissible)
- [ ] Style `::backdrop`

### 2h. error-banner
- [ ] Replace `z-[100]` wrapper with `<dialog>`
- [ ] Style `::backdrop`, add auto-dismiss behavior

## 3. `popover="manual"` for persistent non-modal elements

### 3a. bottom-nav-bar
- [ ] Add `popover="manual"` attribute to nav container element
- [ ] Call `this.navElement.showPopover()` in `attached()` lifecycle
- [ ] Remove `z-30` class
- [ ] Verify nav bar remains visible across route navigations
- [ ] Verify `<dialog>` modals paint above nav bar (later Top Layer insertion)

### 3b. toast-notification
- [ ] Add `popover="manual"` attribute to toast container
- [ ] Call `showPopover()` when toast displayed, `hidePopover()` when dismissed
- [ ] Remove `z-50` class
- [ ] Retain `pointer-events: none` on container with `pointer-events: auto` on toast items
- [ ] Verify toasts paint above dialogs and nav bar

### 3c. coach-mark overlay
- [ ] Add `popover="manual"` to `.coach-mark-overlay` element
- [ ] Call `showPopover()` on activation, `hidePopover()` on dismissal
- [ ] Remove `z-index: 9999` from `coach-mark.css`
- [ ] Verify overlay paints above all other Top Layer elements (latest insertion)
- [ ] Verify click-through on spotlight area still works

## 4. CSS Anchor Positioning for coach-mark tooltip

- [ ] Set `anchor-name: --coach-target` dynamically on the target element via `style.anchorName`
- [ ] Set `position-anchor: --coach-target` on the tooltip element
- [ ] Use `position-area` for placement direction (top/bottom/left/right of target)
- [ ] Add `position-try-fallbacks: flip-block, flip-inline` for viewport edge handling
- [ ] Remove `updatePosition()` JS method that uses `getBoundingClientRect()` for tooltip positioning
- [ ] Remove `ResizeObserver` for tooltip position recalculation (CSS handles this automatically)
- [ ] Keep `getBoundingClientRect()` for spotlight canvas cutout rendering (canvas cannot use CSS positioning)

## 5. Tests

- [ ] Update `event-detail-sheet` tests: query `<dialog>`, verify `[open]` attribute
- [ ] Update `my-artists-page` tests: verify context menu and passion dialogs
- [ ] Update `tickets-page` tests: verify QR dialog and generation overlay
- [ ] Add `bottom-nav-bar` test: verify `popover="manual"` attribute and visibility
- [ ] Add `toast-notification` test: verify popover show/hide lifecycle
- [ ] Add `coach-mark` test: verify popover activation and CSS anchor attributes
- [ ] Verify swipe-to-dismiss on `event-detail-sheet` `<dialog>`
- [ ] Verify dismiss-block suppresses ESC during onboarding DETAIL step

## 6. Verification

- [ ] Run `make check` in frontend repo (lint + test)
- [ ] `grep -rn 'z-index' frontend/src/` — expect 0 results
- [ ] `grep -rn 'z-[0-9]\|z-\[' frontend/src/` — expect 0 Tailwind z-index classes
- [ ] Visual: discover page layers correctly (starfield behind, UI above canvas)
- [ ] Visual: event detail sheet slides up as `<dialog>`, backdrop dims including nav bar
- [ ] Visual: bottom nav bar visible via popover, dialogs paint above it
- [ ] Visual: toast notifications appear above dialogs
- [ ] Visual: coach-mark overlay and tooltip position correctly via Anchor Positioning
- [ ] Visual: coach-mark paints above all other elements
- [ ] Test on mobile Safari and Chrome for popover + fixed position behavior
