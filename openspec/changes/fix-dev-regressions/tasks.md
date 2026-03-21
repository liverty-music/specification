## 1. Fix TicketJourney RPC stub (frontend)

- [x] 1.1 Remove 3 resolve aliases from `vite.config.ts` (ticket_journey_pb, ticket_pb, ticket_journey_service_connect)
- [x] 1.2 Delete `tmp/ticket-journey-stub.js`
- [x] 1.3 Verify `TicketJourneyService` methods resolve from BSR package (`npm run build` succeeds)

## 2. Fix push notification UUID mismatch (backend)

- [x] 2.1 Add `UserRepository` dependency to `PushNotificationHandler` struct and constructor
- [x] 2.2 In `Subscribe`, resolve internal UUID via `userRepo.GetByExternalID(ctx, userID)` before passing to use case
- [x] 2.3 Update DI wiring in `internal/di/` to provide `UserRepository` to `PushNotificationHandler`
- [x] 2.4 Run `mockery` to regenerate mocks if interface changed
- [x] 2.5 Run `make check` to verify lint + tests pass

## 3. Simplify bottom-sheet CE (frontend)

- [x] 3.1 Rewrite `bottom-sheet.html`: remove `div.scroll-wrapper` and `section.sheet-page`, make `dialog` the scroll-snap container with `.dismiss-zone` + `.sheet-body` as direct children, remove `click.trigger` and `scroll.trigger`
- [x] 3.2 Rewrite `bottom-sheet.ts`: remove `onBackdropClick` and `onScroll`; keep `onToggle` for ESC dismiss detection, `dismissableChanged` for auto/manual switching, `openChanged` (showPopover + scrollTo on dialog), and `onScrollEnd`
- [x] 3.3 Rewrite `bottom-sheet.css`: remove `.scroll-wrapper` and `.sheet-page` rules, move scroll-snap properties to `dialog`, add `scroll-timeline: --sheet-scroll block` on `dialog`, add `animation-timeline: --sheet-scroll` on `dialog::backdrop` with `@keyframes backdrop-fade`
- [x] 3.4 Test Scroll-Driven Animation on `::backdrop` in Chrome DevTools — if unsupported, fall back to static opacity
- [x] 3.5 Verify all bottom-sheet consumers render correctly (event-detail-sheet, tickets QR, user-home-selector, hype-notification-dialog, language selector, error-banner)
- [x] 3.6 Run `make check` to verify lint + tests pass

## 4. Update spec (specification)

- [x] 4.1 Archive delta spec into `openspec/specs/bottom-sheet-ce/spec.md`
