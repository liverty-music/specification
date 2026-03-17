## 1. Fullscreen Snap Architecture (CSS)

- [x] 1.1 Change selector to `dialog.event-detail-sheet` for higher specificity against UA stylesheet
- [x] 1.2 Set `inset: 0` with `100dvh` / `100vi` to make dialog fullscreen
- [x] 1.3 Add `translate: 0 0` and `display: block` to override UA popover defaults
- [x] 1.4 Add `.snap-page` (100dvh, `scroll-snap-align: start`, `scroll-snap-stop: always`)
- [x] 1.5 Add `.sheet-page` with `flex-end` to pin card to viewport bottom
- [x] 1.6 Add `.sheet-body` with `max-block-size: 90dvh` and `overflow-y: auto` for long content
- [x] 1.7 Add `--_backdrop-opacity` custom property on `::backdrop` for scroll-driven fade

## 2. DOM restructuring (HTML)

- [x] 2.1 Wrap card in `.snap-page.sheet-page` and dismiss zone in `.snap-page.dismiss-zone`
- [x] 2.2 Place dismiss zone before card in DOM order (swipe down = scroll toward dismissal)
- [x] 2.3 Add `scroll.trigger` alongside `scrollend.trigger` on `.sheet-scroll`
- [x] 2.4 Add `click.trigger="onBackdropClick()"` on `.sheet-page` and `stopPropagation` on `.sheet-body`

## 3. Dismiss behavior (TypeScript)

- [x] 3.1 Set `scrollTop = scrollHeight` on open to start at card page
- [x] 3.2 Update `onScrollEnd` to detect dismiss zone (`scrollTop < maxScroll`)
- [x] 3.3 Add `onScroll` handler for real-time `--_backdrop-opacity` fade
- [x] 3.4 Change `onBackdropClick` to use `scrollTo({ top: 0, behavior: 'smooth' })` for unified dismiss animation

## 4. Verify

- [x] 4.1 Unit tests pass (19/19)
- [x] 4.2 Stylelint passes (0 errors in event-detail-sheet.css)
- [x] 4.3 Playwright: card pinned to viewport bottom (`cardBottom === viewportHeight`)
- [x] 4.4 Playwright: small scroll snaps back, large scroll dismisses
