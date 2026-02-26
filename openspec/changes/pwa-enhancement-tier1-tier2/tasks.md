## 1. VAPID Key Configuration

- [ ] 1.1 Add `VITE_VAPID_PUBLIC_KEY` to frontend `.env` with the dev overlay value
- [ ] 1.2 Update settings push notification toggle to show disabled state when VAPID key is not configured

## 2. PWA Install Prompt

- [ ] 2.1 Create `PwaInstallService` (Aurelia DI singleton) that captures `beforeinstallprompt`, tracks session count in localStorage, and exposes install trigger
- [ ] 2.2 Create `pwa-install-prompt` component with install/dismiss buttons using design system tokens
- [ ] 2.3 Integrate install banner into app shell layout (render above page content, below nav)
- [ ] 2.4 Add localStorage persistence for session count (`liverty-music:session-count`) and dismissal (`liverty-music:install-prompt-dismissed`)

## 3. Concert List Offline Cache

- [ ] 3.1 Add `workbox-strategies` NetworkFirst route in `sw.ts` matching concert-list API endpoint pattern with 3s network timeout
- [ ] 3.2 Configure `concert-api-v1` cache with max 50 entries and 24-hour expiration
- [ ] 3.3 Implement SW-to-client messaging (via `MessageChannel` or response header) to signal when response is from cache
- [ ] 3.4 Add stale-data indicator component to the dashboard UI
- [ ] 3.5 Add empty state message for offline with no cached data

## 4. Background Sync for Artist Operations

- [ ] 4.1 Add `workbox-background-sync` dependency to frontend
- [ ] 4.2 Register `BackgroundSyncPlugin` in `sw.ts` for artist-service RPC endpoint pattern with queue name `artist-ops-queue` and 7-day max retention
- [ ] 4.3 Verify artist follow/unfollow/passion-level requests are intercepted by SW (Connect transport uses `fetch()`)
- [ ] 4.4 Add graceful fallback for browsers without Background Sync support

## 5. Periodic Concert Data Refresh

- [ ] 5.1 Register `periodicSync` tag `concert-refresh` with 12-hour minimum interval (feature-detect before registration)
- [ ] 5.2 Add `periodicsync` event handler in `sw.ts` that fetches concert-list endpoint and updates `concert-api-v1` cache
- [ ] 5.3 Verify graceful degradation on unsupported browsers (no errors, no warnings)

## 6. ZK Circuit File Pre-Cache

- [ ] 6.1 Add `install` event handler in `sw.ts` that pre-caches `/ticketcheck.wasm` and `/ticketcheck.zkey` into `zk-circuits-v1` cache
- [ ] 6.2 Skip pre-cache if files are already in cache (avoid unnecessary re-fetch on SW update)
- [ ] 6.3 Ensure SW activation is not blocked if pre-cache fetch fails (catch and log warning)

## 7. Playwright E2E Tests

- [ ] 7.1 Create Playwright test: PWA install prompt — first session shows no banner, set `liverty-music:session-count` to 1 + dispatch synthetic `beforeinstallprompt` → banner visible, click dismiss → `liverty-music:install-prompt-dismissed` set, reload → banner not shown
- [ ] 7.2 Create Playwright test: PWA install prompt — click "Install" button → verify deferred prompt's `prompt()` is called (mock via `page.evaluate`)
- [ ] 7.3 Create Playwright test: Offline concert cache — navigate to dashboard (online), verify concert data rendered, set `context.setOffline(true)`, reload → cached data rendered + stale-data indicator visible
- [ ] 7.4 Create Playwright test: Offline concert cache empty state — set `context.setOffline(true)` without prior cache, navigate to dashboard → empty state message displayed (no infinite spinner)
- [ ] 7.5 Create Playwright test: Settings push toggle disabled — launch app without `VITE_VAPID_PUBLIC_KEY` → push notification toggle is disabled with helper text
- [ ] 7.6 Create Playwright test: ZK circuit pre-cache — wait for SW registration, query Cache API via `page.evaluate(() => caches.open('zk-circuits-v1').then(c => c.keys()))` → verify `ticketcheck.wasm` and `ticketcheck.zkey` entries exist

## 8. Manual Verification

- [ ] 8.1 Verify push notification subscribe/unsubscribe works locally with VAPID key set
- [ ] 8.2 Test background sync: follow artist offline, restore connectivity — operation replayed (not automatable via Playwright)
- [ ] 8.3 Test periodic sync: install PWA, verify `periodicSync` registration via DevTools > Application > Periodic Background Sync
