## 1. Fix Artist API route in sw.ts

- [x] 1.1 Change Artist API route strategy from `NetworkFirst` to `NetworkOnly` in `src/sw.ts`
- [x] 1.2 Update workbox-strategies import: replace `NetworkFirst` with `NetworkOnly`

## 2. Remove dead Concert API code from sw.ts

- [x] 2.1 Remove `CONCERT_CACHE` constant
- [x] 2.2 Remove Concert API `registerRoute` block
- [x] 2.3 Remove `periodicsync` event listener

## 3. Remove dead Concert API code from main.ts

- [x] 3.1 Remove `periodicSync.register('concert-refresh', ...)` call from SW registration
- [x] 3.2 Remove `REFRESH_CONCERT_CACHE` message event listener (including the dynamic `oidc-client-ts` import)

## 4. Verify

- [x] 4.1 Run `make check` (lint + test) in frontend
- [x] 4.2 Run `npm run build` to verify SW bundle compiles
