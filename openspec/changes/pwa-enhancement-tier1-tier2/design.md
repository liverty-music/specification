## Context

The Liverty Music frontend is an Aurelia 2 PWA built with Vite. The Service Worker (`src/sw.ts`) uses Workbox with `injectManifest` strategy. Current SW capabilities are limited to app-shell precaching, ZK circuit CacheFirst caching, and push notification handling.

The backend exposes Connect-RPC endpoints consumed by the frontend. Push notification infrastructure (VAPID, `webpush-go`, `push_subscriptions` table) is fully implemented. The VAPID public key is available in the dev K8s overlay (`BNg-zJP4IiX11Cz1dghWll0mwBnMV6oeOSSVsYyOK2l8NFAqN9xHFSTS_W3_oXO4k3BlMyYLjkMUE-uA7LABGHo`) but missing from the frontend `.env`.

## Goals / Non-Goals

**Goals:**
- Enable push notifications in local development by configuring VAPID keys.
- Provide a non-intrusive PWA install prompt on the second user session.
- Allow offline browsing of previously loaded concert data on the dashboard.
- Queue artist operations (follow/unfollow/passion) when offline and replay on reconnection.
- Keep concert data fresh via periodic background sync.
- Guarantee ZK circuit files are cached on first SW install (no cold-cache penalty).

**Non-Goals:**
- Offline QR code generation (requires Merkle path pre-fetch design — separate change).
- Offline authentication or token refresh.
- Full offline-first app architecture (IndexedDB-backed data layer).
- Push notification content customization or scheduling changes.
- Backend API changes.

## Decisions

### D1: VAPID key in `.env`

Add `VITE_VAPID_PUBLIC_KEY` to the frontend `.env` using the dev overlay value. This is a public key embedded in the client bundle at build time — no secret exposure risk.

**Alternative**: Generate a separate local keypair → Rejected: adds complexity, dev and deployed environments should use the same keypair for consistent subscription testing.

### D2: Install prompt — `beforeinstallprompt` + localStorage session counter

Capture the `beforeinstallprompt` event in a new Aurelia service (`PwaInstallService`). Persist a session count in `localStorage` (`liverty-music:session-count`). Show a custom banner component on the second session.

The banner renders inside the app shell's main content area (not as a system-level notification) and can be dismissed. Dismissal is persisted in `localStorage` (`liverty-music:install-prompt-dismissed`).

**Alternative**: Use the browser's native mini-infobar → Rejected: limited customization and inconsistent across browsers.

### D3: Concert list caching — Workbox `NetworkFirst` with `StaleWhileRevalidate` fallback

Register a Workbox route in `sw.ts` matching the concert-list API endpoint pattern (`*/liverty_music.rpc.concert.v1.ConcertService/*`). Use `NetworkFirst` strategy with a 3-second network timeout, falling back to cached response.

Cache name: `concert-api-v1`. Max entries: 50. Max age: 24 hours.

The dashboard UI shows a subtle "Showing cached data" indicator when the response is served from cache (detectable via response header or SW message channel).

**Alternative**: Cache at the application layer with IndexedDB → Rejected: Workbox route-level caching is simpler, requires no app-layer changes, and integrates with existing SW architecture.

### D4: Background Sync for artist operations — Workbox `BackgroundSyncPlugin`

Use `workbox-background-sync` to wrap the artist-service RPC calls. When a follow/unfollow/passion-level mutation fails due to network error, the request is queued in IndexedDB (managed by Workbox) and retried when connectivity returns.

Queue name: `artist-ops-queue`. Max retention: 7 days.

This requires the artist service to make requests via `fetch()` (which the SW can intercept) rather than direct Connect-RPC transport. The Connect transport already uses `fetch()` under the hood, so no changes are needed — the SW intercepts failed fetch requests.

**Alternative**: Custom IndexedDB queue with manual retry → Rejected: Workbox BackgroundSync handles retry scheduling, IndexedDB storage, and SW lifecycle automatically.

### D5: Periodic Background Sync — `periodicSync` API registration

Register a periodic sync tag `concert-refresh` with a minimum interval of 12 hours. The SW handler fetches the concert-list endpoint and updates the `concert-api-v1` cache.

This API requires the PWA to be installed and has limited browser support (Chromium only). It degrades gracefully — if unsupported, the app relies on NetworkFirst caching on active use.

**Alternative**: Push-based refresh (server sends push to trigger client fetch) → Rejected: adds backend complexity and consumes push subscription bandwidth.

### D6: Circuit file pre-cache — SW `install` event

Add the circuit file URLs (`/ticketcheck.wasm`, `/ticketcheck.zkey`) to the SW install event handler. Use `cache.addAll()` to populate the `zk-circuits-v1` cache during installation. This ensures the files are available before the user first needs them.

The existing `CacheFirst` route handler continues to serve them from cache on subsequent requests.

**Alternative**: Add to Workbox precache manifest → Rejected: circuit files are not part of the Vite build output; they're static assets. Explicit `cache.addAll()` is more appropriate.

## Risks / Trade-offs

- **Periodic Sync browser support**: Only Chromium-based browsers support `periodicSync`. Safari and Firefox users won't get background refresh. → Mitigation: Feature-detect and degrade to NetworkFirst on active use.
- **Background Sync replay ordering**: If a user follows then unfollows the same artist while offline, both requests queue. → Mitigation: Workbox replays in FIFO order, so the final state is correct. The backend is idempotent for follow/unfollow.
- **Concert cache staleness**: Cached concert data could be up to 24 hours old. → Mitigation: UI indicator ("Showing cached data") and NetworkFirst strategy ensures fresh data is preferred when online.
- **Circuit pre-cache on slow networks**: Fetching 5.2 MB during SW install could delay activation. → Mitigation: Use `event.waitUntil()` with the pre-cache but don't block on failure — fall back to runtime CacheFirst.
- **Install prompt fatigue**: Showing a banner could annoy users. → Mitigation: Only shown once on second session, dismissible, and respects `liverty-music:install-prompt-dismissed`.

## Open Questions

- Should the stale-data indicator auto-dismiss when fresh data arrives, or persist until the user dismisses it?
- What should the minimum interval for periodic sync be? 12 hours is conservative; could be reduced to 6 hours.
