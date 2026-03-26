## Why

The Service Worker throws `TypeError: Failed to execute 'put' on 'Cache': Request method 'POST' is unsupported` on every Artist API call. The Cache API only supports GET requests, but Connect-RPC sends all RPCs as POST. The `NetworkFirst` strategy on the Artist API route attempts `cache.put()` on the POST response, causing this error.

Additionally, the Concert API SW route was registered without a `'POST'` method filter, so it never matches actual Connect-RPC requests and is entirely dead code (along with the associated `periodicSync` handler and `REFRESH_CONCERT_CACHE` message handler in `main.ts`).

## What Changes

- **Artist API route**: Change strategy from `NetworkFirst` to `NetworkOnly` so no cache write is attempted. `BackgroundSyncPlugin` is retained for offline operation queuing.
- **Concert API route**: Remove the dead `registerRoute` for ConcertService, the `CONCERT_CACHE` constant, the `periodicSync` event listener in `sw.ts`, and the `REFRESH_CONCERT_CACHE` message handler + `periodicSync.register()` call in `main.ts`.
- **Workbox import**: Remove unused `NetworkFirst` import from `workbox-strategies` (only `CacheFirst` and `NetworkOnly` remain).

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

(none - this is a bug fix removing non-functional code; no spec-level behavior changes)

## Impact

- **Frontend (`src/sw.ts`)**: Strategy change + dead code removal
- **Frontend (`src/main.ts`)**: Remove `periodicSync` registration and `REFRESH_CONCERT_CACHE` message listener
- **No backend or proto changes required**
- **Future**: Concert API offline caching will require a separate change introducing `useHttpGet` on the Connect transport (cross-repo: specification + frontend + backend)
