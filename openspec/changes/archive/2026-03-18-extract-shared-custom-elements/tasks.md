## 1. Create `<bottom-sheet>` CE

- [x] 1.1 Create `components/bottom-sheet/bottom-sheet.ts` — ViewModel with `@bindable open`, `@bindable dismissable`, popover API, scroll-snap dismiss, backdrop opacity tracking, focus management, toggle event handling, detach cleanup
- [x] 1.2 Create `components/bottom-sheet/bottom-sheet.html` — `<dialog>` with scroll-snap container, dismiss zone, sheet-page, sheet-body, handle-bar, `<au-slot>`
- [x] 1.3 Create `components/bottom-sheet/bottom-sheet.css` — Extract shared dialog/backdrop/handle-bar/transition CSS from event-detail-sheet.css into `@layer block` with `@scope (bottom-sheet)`
- [x] 1.4 Register `<bottom-sheet>` in `main.ts`

## 2. Create `<loading-spinner>` CE

- [x] 2.1 Create `components/loading-spinner/loading-spinner.ts` — ViewModel with `@bindable size: 'sm' | 'md' | 'lg'`
- [x] 2.2 Create `components/loading-spinner/loading-spinner.html` — `<output role="status" aria-busy="true">` with spinner element
- [x] 2.3 Create `components/loading-spinner/loading-spinner.css` — Spinner block styles with size variants via `data-size`, reduced motion support
- [x] 2.4 Register `<loading-spinner>` in `main.ts`

## 3. Create `<toast>` CE

- [x] 3.1 Create `components/toast/toast.ts` — ViewModel with `@bindable open`, popover="manual" management, `toast-closed` event dispatch
- [x] 3.2 Create `components/toast/toast.html` — `<dialog popover="manual">` with `<au-slot>` for content
- [x] 3.3 Create `components/toast/toast.css` — Top-positioned popover styles, entry/exit animation via `@starting-style`
- [x] 3.4 Register `<toast>` in `main.ts`

## 4. Rename `toast-notification` → `snack-bar`

- [x] 4.1 Rename `components/toast-notification/` directory to `components/snack-bar/`
- [x] 4.2 Rename all files: `toast-notification.*` → `snack-bar.*`
- [x] 4.3 Rename ViewModel class `ToastNotification` → `SnackBar`
- [x] 4.4 Rename `Toast` event class to `Snack` in `snack.ts` (was `toast.ts`)
- [x] 4.5 Update all import references across the codebase (grep for `toast-notification`, `Toast`, `toast.ts`)
- [x] 4.6 Update `main.ts` registration
- [x] 4.7 Update CSS `@scope` selector from `toast-notification` to `snack-bar`

## 5. Simplify `<state-placeholder>`

- [x] 5.1 Remove `title`, `description`, `ctaLabel` bindables from `state-placeholder.ts` — keep only `@bindable icon`
- [x] 5.2 Update `state-placeholder.html` — remove conditional `<h2>` and `<p>`, keep only `<svg-icon>` + `<au-slot>`
- [x] 5.3 Remove `.state-title` and `.state-desc` from `state-placeholder.css`
- [x] 5.4 Update all consumers to use slotted content instead of bindables (dashboard-route, tickets-route, my-artists-route)

## 6. Migrate `event-detail-sheet` to `<bottom-sheet>`

- [x] 6.1 Replace `<dialog>` in event-detail-sheet.html with `<bottom-sheet open.bind="isOpen" dismissable.bind="isDismissable">`
- [x] 6.2 Move sheet content (hero, header, details, actions) into the `<au-slot>`
- [x] 6.3 Remove dialog/backdrop/handle-bar/scroll-snap CSS from event-detail-sheet.css — keep only content-specific styles (hero, artist-header, detail-rows, buttons)
- [x] 6.4 Simplify event-detail-sheet.ts — remove `showPopover()`/`hidePopover()`, scroll tracking, toggle event, popstate handling; listen for `sheet-closed` event instead
- [x] 6.5 Handle history pushState/replaceState in event-detail-sheet.ts (CE-external concern)

## 7. Migrate `user-home-selector` to `<bottom-sheet>`

- [x] 7.1 Replace `<dialog>` in user-home-selector.html with `<bottom-sheet open.bind="isOpen" dismissable.bind="!required">`
- [x] 7.2 Move selector content (handle, steps, grids) into the `<au-slot>`
- [x] 7.3 Remove dialog/backdrop/handle-bar CSS from user-home-selector.css — keep only content-specific styles (selector-grid, selector-btn, etc.)
- [x] 7.4 Simplify user-home-selector.ts — remove `showModal()`/`close()`, `handleBackdropClick()`, `handleCancel()`; use `open` binding + `sheet-closed` event

## 8. Migrate `settings-route` language selector to `<bottom-sheet>`

- [x] 8.1 Replace inline `<dialog class="language-selector">` in settings-route.html with `<bottom-sheet open.bind="languageSelectorOpen">`
- [x] 8.2 Move language list content into the `<au-slot>`
- [x] 8.3 Delete all `dialog.language-selector` CSS from settings-route.css (~140 lines)
- [x] 8.4 Simplify settings-route.ts — remove `openLanguageSelector()`/`closeLanguageSelector()` dialog management; use `open` binding

## 9. Migrate `hype-notification-dialog` to `<bottom-sheet>`

- [x] 9.1 Replace `<dialog>` in hype-notification-dialog.html with `<bottom-sheet open.bind="active">`
- [x] 9.2 Move notification content into the `<au-slot>`
- [x] 9.3 Delete all dialog CSS from hype-notification-dialog.css — keep only content-specific styles
- [x] 9.4 Simplify hype-notification-dialog.ts — remove `showModal()`/`close()`; use `open` binding

## 10. Migrate `error-banner` to `<bottom-sheet>`

- [x] 10.1 Replace `<dialog>` in error-banner.html with `<bottom-sheet open.bind="errorBoundary.currentError" dismissable.bind="false">`
- [x] 10.2 Move error content into the `<au-slot>`
- [x] 10.3 Delete dialog CSS from error-banner.css — keep only content-specific styles
- [x] 10.4 Simplify error-banner.ts — remove `showModal()`/`close()` in `@watch`; use `open` binding

## 11. Migrate `tickets-route` dialogs to `<bottom-sheet>`

- [x] 11.1 Replace generating-dialog and qr-dialog in tickets-route.html with `<bottom-sheet>` instances
- [x] 11.2 Delete `.center-dialog`, `.dialog-card`, `.dialog-title`, `.dialog-desc`, `.dialog-hint`, `.dialog-close-btn` CSS from tickets-route.css
- [x] 11.3 Delete `.state-center`, `.spinner`, `.spinner-lg`, `.spinner-sm`, `.state-text` CSS from tickets-route.css
- [x] 11.4 Replace inline loading markup with `<state-placeholder>` + `<loading-spinner>`

## 12. Migrate `notification-prompt` to `<toast>`

- [x] 12.1 Replace `<dialog popover="manual">` in notification-prompt.html with `<toast open.bind="isVisible">`
- [x] 12.2 Move prompt content (emoji, title, description, buttons) into the `<au-slot>`
- [x] 12.3 Delete all popover/banner CSS from notification-prompt.css — keep only content-specific styles
- [x] 12.4 Simplify notification-prompt.ts — remove `showPopover()`/`hidePopover()` management

## 13. Migrate `pwa-install-prompt` to `<toast>`

- [x] 13.1 Replace `<dialog popover="manual">` in pwa-install-prompt.html with `<toast open.bind="isVisible">`
- [x] 13.2 Move prompt content (icon, title, description, buttons) into the `<au-slot>`
- [x] 13.3 Delete all popover/banner CSS from pwa-install-prompt.css — keep only content-specific styles

## 14. Migrate `my-artists-route` spinner/state

- [x] 14.1 Replace inline spinner markup with `<loading-spinner>`
- [x] 14.2 Delete `.spinner` CSS from my-artists-route.css (`.state-center` kept for loading layout)
- [x] 14.3 Update empty state to use simplified `<state-placeholder icon="music">` with slotted content (already using slots)

## 15. Verification

- [x] 15.1 Run `make check` — lint + typecheck + unit tests pass (pre-existing warnings only; our changes clean)
- [x] 15.2 Run `npm run build` — production build succeeds
- [x] 15.3 Manual smoke test: open/close bottom-sheet on dashboard (event detail), settings (home selector, language selector), my-artists (hype notification), tickets (QR dialog)
- [x] 15.4 Manual smoke test: notification-prompt and pwa-install-prompt display correctly as `<toast>`
- [x] 15.5 Manual smoke test: snack-bar (renamed) still displays correctly
- [x] 15.6 Manual smoke test: loading spinners render at correct sizes
- [x] 15.7 Verify no orphaned CSS — grep for deleted class names across all files
