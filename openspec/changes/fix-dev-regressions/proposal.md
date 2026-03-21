## Why

Three bugs are visible on the dev environment (dev.liverty-music.app) as of 2026-03-21: TicketJourney RPC calls fail because Vite aliases override generated BSR code with an empty stub, push notification subscribe fails due to a Zitadel-to-UUID type mismatch in the backend, and the bottom-sheet's scroll-down and backdrop-tap dismiss mechanisms are broken. The bottom-sheet's implementation is also overly complex with three competing dismiss paths and JS-driven backdrop opacity — this should be simplified using modern CSS (Scroll-Driven Animations) and the Popover API's native light dismiss.

## What Changes

- **Frontend**: Remove stale Vite resolve aliases for TicketJourneyService stub in `vite.config.ts` and delete `tmp/ticket-journey-stub.js`
- **Backend**: Add `GetByExternalID` user lookup in `PushNotificationHandler.Subscribe` to convert Zitadel numeric ID to internal UUID before database insert
- **Frontend**: Simplify `<bottom-sheet>` custom element — remove `.sheet-page` wrapper and `onBackdropClick` JS hack, replace JS-driven `onScroll` backdrop opacity with CSS Scroll-Driven Animations, keep `popover="auto"` light dismiss as-is

## Capabilities

### New Capabilities

_(none)_

### Modified Capabilities

- `bottom-sheet-ce`: Replace JS-driven backdrop opacity with CSS Scroll-Driven Animations; remove `onBackdropClick` and `.sheet-page` wrapper; simplify DOM to dialog > scroll-wrapper > dismiss-zone + sheet-body

## Impact

- **Frontend `vite.config.ts`**: Remove 3 resolve alias entries + delete stub file
- **Frontend `src/components/bottom-sheet/`**: Rewrite .ts, .html, .css (fewer lines overall)
- **Backend `internal/adapter/rpc/push_notification_handler.go`**: Add UserRepository dependency, wire via DI
- **Backend `internal/usecase/push_notification_uc.go`**: No change (receives correct UUID)
- **Backend `internal/di/`**: Update Wire provider set for PushNotificationHandler
