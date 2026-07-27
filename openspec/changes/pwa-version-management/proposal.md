## Why

Installed PWA users can be silently stuck on outdated code indefinitely — the current implementation uses a bare `navigator.serviceWorker.register()` with no update lifecycle handling, so a waiting service worker never activates until the user force-quits the app. Users also have no way to know what version they are running, which makes bug reports and support conversations harder than they need to be.

## What Changes

- Replace the bare SW registration in `main.ts` with `virtual:pwa-register` from `vite-plugin-pwa`, which handles update detection, `controllerchange`-based single-shot reload, and reloop guarding out of the box.
- Add `SKIP_WAITING` message handler and `clients.claim()` to `sw.ts` to complete the update handoff on the SW side.
- Show a persistent non-blocking update toast ("新しいバージョンが利用可能です [更新]") when a waiting SW is detected; the user controls when reload happens.
- Silent auto-apply only on first paint before any user interaction (no controller = initial install or brand-new tab; nothing to lose).
- Trigger `registration.update()` on boot and on `visibilitychange:visible` so PWA users who never close the app still receive updates promptly.
- Add `releaseVersion` field to the `AppConfig` schema and to every per-environment `config.json` ConfigMap; the prod pin-bump workflow writes the version automatically.
- Add a version display row to the Settings screen showing `releaseVersion` (from config.json) and a build-time SHA (injected via vite `define`).

## Capabilities

### New Capabilities

- `pwa-update-lifecycle`: Service worker update detection, user-controlled apply flow, and boot-time silent apply.

### Modified Capabilities

- `frontend-runtime-config`: Add `releaseVersion` field to the `AppConfig` schema.
- `settings`: Add app version display (release version + build SHA) to the Settings screen.
- `prod-image-pipeline`: Pin-bump workflow writes `releaseVersion` to config.json ConfigMaps as part of each release.

## Impact

- **frontend repo**: `main.ts` (SW registration), `sw.ts` (SKIP_WAITING + clients.claim), `vite.config.ts` (`define: __BUILD_SHA__`), `settings-route.ts/.html`, `shared/config/app-config.ts` (AppConfig shape), new update-toast component or snack variant, `virtual:pwa-register` import.
- **cloud-provisioning repo**: Per-environment `config.json` ConfigMaps (dev + prod) gain `releaseVersion` field; prod pin-bump workflow (`bump-prod-pin.yaml` or equivalent) writes the new field on each release.
- **No backend proto changes.** No new RPC. No BSR publish required.
