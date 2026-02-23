## 1. Migrate region-setup-sheet to `<dialog>`

- [x] 1.1 Replace the template's outer `<div>` with a `<dialog>` element; remove the manual backdrop `<div>`, all `z-40`/`z-50` classes, and the `translate-y-full`/`translate-y-0` conditional class
- [x] 1.2 Add CSS for `<dialog>` bottom-sheet positioning (`margin: 0 0 0 auto`, `max-height: 80vh`, `inset-inline: 0`, `inset-block-end: 0`), `::backdrop` styling (OKLCH dark overlay + blur), and `@starting-style` slide-up/fade animation with `prefers-reduced-motion` guard
- [x] 1.3 Update the TypeScript to call `dialogElement.showModal()` / `dialogElement.close()` instead of toggling `isOpen` for DOM visibility; sync `isOpen` state from the `close` event
- [x] 1.4 Implement click-outside-to-close by listening for `click` on `<dialog>` and checking `event.target === dialogElement`

## 2. Migrate area-selector-sheet to `<dialog>`

- [x] 2.1 Replace the template's outer `<div>` with a `<dialog>` element; remove manual backdrop `<div>`, all `z-40`/`z-50` classes, the `inert.bind`, and the `translate-y-full`/`translate-y-0` conditional class
- [x] 2.2 Add CSS for `<dialog>` bottom-sheet positioning and `::backdrop` styling (same pattern as region-setup-sheet)
- [x] 2.3 Update the TypeScript to call `dialogElement.showModal()` / `dialogElement.close()`; handle the `cancel` event to reset `selectedRegion` state
- [x] 2.4 Implement click-outside-to-close via the same `<dialog>` click target check pattern

## 3. Test updates

- [x] 3.1 Update region-setup-sheet tests: change element queries from `<div>` to `<dialog>`, remove z-index assertions, verify `showModal()`/`close()` calls
- [x] 3.2 Update area-selector-sheet tests: change element queries from `<div>` to `<dialog>`, remove z-index assertions, verify `showModal()`/`close()` calls and `cancel` event handling

## 4. Verification

- [x] 4.1 Run linter and typecheck (`npm run lint && npm run typecheck`)
- [x] 4.2 Run full test suite (`npm test`)
- [x] 4.3 Manually verify on mobile viewport: area dialog renders above bottom nav bar without z-index, backdrop dims entire page, ESC closes dialog
