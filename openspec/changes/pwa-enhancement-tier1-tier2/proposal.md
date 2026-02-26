## Why

The PWA infrastructure (Service Worker, manifest, push notification pipeline) is in place but several high-impact capabilities remain unused. Users attending live events often face unreliable network conditions, making offline access to concert schedules and reliable push notifications critical. Additionally, the spec-required PWA install prompt is unimplemented, and the ZK circuit files (5.2 MB) lack guaranteed pre-caching on first load.

## What Changes

- **VAPID key local configuration**: Add `VITE_VAPID_PUBLIC_KEY` to the frontend `.env` so push notifications work in local development.
- **PWA install prompt**: Capture `beforeinstallprompt` and display a custom "Add to Home Screen" prompt on the user's second session, as required by the frontend-onboarding-flow spec.
- **Concert list offline cache**: Apply a NetworkFirst caching strategy to the Live Highway dashboard API responses so users can browse events without connectivity.
- **Background Sync for artist operations**: Queue follow/unfollow/passion-level changes when offline and replay them automatically on reconnection.
- **Periodic concert data refresh**: Use Periodic Background Sync to keep followed-artist concert data fresh without requiring the user to open the app.
- **Guaranteed circuit file pre-cache**: Eagerly fetch `.wasm` and `.zkey` files during the Service Worker `install` event so QR proof generation never hits a cold-cache penalty.

## Capabilities

### New Capabilities
- `pwa-install-prompt`: Captures `beforeinstallprompt`, persists session count, and shows a non-intrusive install banner on the second visit.
- `offline-concert-cache`: NetworkFirst caching of concert-list API responses with stale-data indicator in the UI.
- `background-sync-artist-ops`: Queues artist follow/unfollow/passion-level mutations in IndexedDB and replays via Background Sync API on reconnection.
- `periodic-concert-sync`: Registers a Periodic Background Sync task that refreshes concert data for followed artists.
- `circuit-precache`: Pre-caches ZK circuit artifacts (`ticketcheck.wasm`, `ticketcheck.zkey`) during SW install event.

### Modified Capabilities
- `settings`: Add visual feedback when push notifications are unavailable due to missing VAPID configuration.
- `app-shell-layout`: Render the PWA install banner within the app shell's notification area.

## Impact

- **Frontend (Aurelia 2 + Vite PWA)**:
  - `src/sw.ts` — new caching routes, install-event pre-cache, Background Sync handler, Periodic Sync handler.
  - New component `pwa-install-prompt` — install banner UI.
  - `src/services/push-service.ts` — graceful handling when VAPID key is absent.
  - Dashboard component — stale-data indicator for cached concert lists.
  - Artist operation services — IndexedDB queue + retry logic.
- **Frontend `.env`**: New `VITE_VAPID_PUBLIC_KEY` entry.
- **Backend**: No changes required — existing RPC endpoints are sufficient.
- **Dependencies**: Potentially `workbox-background-sync` (Workbox plugin for Background Sync).
