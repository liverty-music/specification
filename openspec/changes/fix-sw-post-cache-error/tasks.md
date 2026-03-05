## 1. Fix Artist API route in sw.ts

- [ ] 1.1 Change Artist API route strategy from `NetworkFirst` to `NetworkOnly` in `src/sw.ts`
- [ ] 1.2 Update workbox-strategies import: replace `NetworkFirst` with `NetworkOnly`

## 2. Remove dead Concert API code from sw.ts

- [ ] 2.1 Remove `CONCERT_CACHE` constant
- [ ] 2.2 Remove Concert API `registerRoute` block
- [ ] 2.3 Remove `periodicsync` event listener

## 3. Remove dead Concert API code from main.ts

- [ ] 3.1 Remove `periodicSync.register('concert-refresh', ...)` call from SW registration
- [ ] 3.2 Remove `REFRESH_CONCERT_CACHE` message event listener (including the dynamic `oidc-client-ts` import)

## 4. Verify

- [ ] 4.1 Run `make check` (lint + test) in frontend
- [ ] 4.2 Run `npm run build` to verify SW bundle compiles
