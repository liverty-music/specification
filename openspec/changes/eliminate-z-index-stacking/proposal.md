## Why

The Liverty Music frontend contains 26 `z-index` declarations across 11 files despite the `onboarding-guidance` spec explicitly prohibiting z-index in the discovery page CSS. Previous changes removed some instances but left exceptions for `bottom-nav-bar` (`z-30`), `coach-mark` (`z-9999`), and `discover-page.css` (7 instances). Modern Web Platform APIs (Popover API, CSS Anchor Positioning, `<dialog>`, `isolation: isolate`) — all Baseline 2026 — eliminate the need for any z-index. The Top Layer replaces numeric z-index wars with insertion-order stacking, and `isolation: isolate` handles component-internal layering.

## What Changes

- Remove all 7 `z-index` declarations from `discover-page.css`; use `isolation: isolate` for explicit stacking context
- Remove all 6 `z-index` declarations from `loading-sequence.css`; use `isolation: isolate` (also handled by `remove-loading-sequence` change)
- Migrate `event-detail-sheet`, `my-artists-page` overlays, `tickets-page` overlays, `signup-modal`, and `error-banner` from z-index overlays to `<dialog>` with `showModal()` Top Layer promotion
- Migrate `bottom-nav-bar` from `z-30` to `popover="manual"` for Top Layer promotion without focus trapping
- Migrate `toast-notification` from `z-50` to `popover="manual"` for Top Layer promotion with click-through
- Migrate `coach-mark` from `z-9999` to `popover="manual"` + CSS Anchor Positioning for tooltip placement
- Remove `z-20` from `live-highway` sticky date separator; use `isolation: isolate` on scroll container
- Achieve zero z-index declarations in the entire frontend codebase

## Capabilities

### New Capabilities

- `top-layer-architecture`: Document the Top Layer insertion order contract (bottom-nav < dialogs < toasts < coach-mark) as the replacement for z-index stacking

### Modified Capabilities

- `onboarding-guidance`: Enforce the existing "no z-index" requirement and extend it to the entire codebase
- `concert-detail`: Event detail bottom sheet migrates from z-index overlay to `<dialog>` Top Layer
- `my-artists`: Context menu and passion explanation modals migrate to `<dialog>` Top Layer
- `app-shell-layout`: Bottom nav bar migrates from `z-30` to `popover="manual"` Top Layer; toast migrates to `popover="manual"`; no z-index exceptions remain
- `onboarding-tutorial`: Coach mark migrates from `z-9999` to `popover="manual"` + CSS Anchor Positioning

## Impact

- `frontend/src/routes/discover/discover-page.css` — Remove 7 z-index, add `isolation: isolate`
- `frontend/src/routes/onboarding-loading/loading-sequence.css` — Remove 6 z-index, add `isolation: isolate`
- `frontend/src/components/live-highway/event-detail-sheet.html` — Convert to `<dialog>`
- `frontend/src/components/live-highway/event-detail-sheet.ts` — Add `showModal()`/`close()` lifecycle
- `frontend/src/routes/my-artists/my-artists-page.html` — Convert overlays to `<dialog>`
- `frontend/src/routes/my-artists/my-artists-page.ts` — Add dialog lifecycle management
- `frontend/src/routes/tickets/tickets-page.html` — Convert overlays to `<dialog>`
- `frontend/src/routes/tickets/tickets-page.ts` — Add dialog lifecycle management
- `frontend/src/components/signup-modal/signup-modal.html` — Convert to `<dialog>`
- `frontend/src/components/error-banner/error-banner.html` — Convert to `<dialog>`
- `frontend/src/components/bottom-nav-bar/bottom-nav-bar.html` — Add `popover="manual"`, remove `z-30`
- `frontend/src/components/bottom-nav-bar/bottom-nav-bar.ts` — Add `showPopover()` on attached
- `frontend/src/components/toast-notification/toast-notification.html` — Add `popover="manual"`, remove `z-50`
- `frontend/src/components/toast-notification/toast-notification.ts` — Add `showPopover()`/`hidePopover()` lifecycle
- `frontend/src/components/coach-mark/coach-mark.css` — Remove `z-index: 9999`
- `frontend/src/components/coach-mark/coach-mark.ts` — Add `showPopover()`, replace `getBoundingClientRect()` with CSS Anchor Positioning
- `frontend/src/components/coach-mark/coach-mark.html` — Add `popover="manual"`, CSS anchor attributes
- `frontend/src/components/live-highway/live-highway.html` — Add `isolation: isolate` to scroll container, remove `z-20`
