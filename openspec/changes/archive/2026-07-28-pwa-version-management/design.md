## Context

The frontend is a vite-plugin-pwa (injectManifest strategy) PWA. The current SW registration is a bare `navigator.serviceWorker.register('/sw.js')` in `main.ts` with no update lifecycle handling. A waiting service worker sits indefinitely until the user force-quits — especially problematic on installed standalone PWAs. The existing `Snack` component (with `action` and `duration` options) and `ResumeRevalidator` (visibilitychange hook) are reusable building blocks.

Release version identity is split: the build-time image digest is available as a git SHA at build time, but the semver release label (`v1.26.0`) is only determined at release time (retag via `crane copy`). The per-environment `config.json` ConfigMap is the correct carrier for the release label because the pin-bump workflow already touches cloud-provisioning on each release.

## Goals / Non-Goals

**Goals:**
- Users running an outdated installed PWA receive and can apply updates without force-quitting.
- Users can see the current release version and build identity in Settings for support purposes.
- The update UX never interrupts an ongoing interaction (no modal, no surprise reload).
- Boot-time: if a waiting SW is detected before any user interaction, apply silently (nothing to lose).

**Non-Goals:**
- Kill-switch / forced minimum-version enforcement (deferred; hybrid flow makes it unnecessary for now).
- "What's new" release notes UI (separate future capability).
- Offline app-shell fallback (intentional non-goal per the `frontend-runtime-config` spec rationale).
- iOS Safari quirks beyond standard SW lifecycle (no additional workarounds in scope).

## Decisions

### D1 — Use `virtual:pwa-register` for client-side SW management

**Decision:** Replace the bare `navigator.serviceWorker.register()` in `main.ts` with `registerSW` from `virtual:pwa-register` (already available via the installed `vite-plugin-pwa`), with `registerType: 'prompt'`.

**Rationale:** The virtual module handles `updatefound → statechange → installed+controller` detection, the single-shot page reload on update (via an internal `controlling` event listener that calls `window.location.reload()` when `isUpdate: true`), and the `SKIP_WAITING` postMessage round-trip — all of which are correct-but-subtle to hand-roll. The injectManifest strategy still keeps the hand-written `sw.ts`; only the client-side registration moves to the virtual module. No new dependency is introduced.

**Critical implication:** Because `virtual:pwa-register` already wires the `controlling` → `location.reload()` handler internally, **no manual `controllerchange` listener should be added**. Adding one alongside the library's handler causes a double-reload on every SW update.

**Alternative considered:** Continue with hand-written registration + custom updatefound listener. Rejected: the reload-once guard and the detection chain (updatefound → statechange → installed && controller) are boilerplate we do not need to maintain, and hand-rolling the guard is a common source of reloop bugs.

SW-side additions required in `sw.ts`:
```
// In message handler: if (e.data?.type === 'SKIP_WAITING') self.skipWaiting()
// In activate handler: event.waitUntil(Promise.all([self.clients.claim(), flushInteractionStash()]))
// NOTE: Promise.all is required — replacing the existing waitUntil call drops flushInteractionStash
```

### D2 — Update UX: persistent Snack with [更新] action, silent apply on boot only

**Decision:** When a waiting SW is detected after user interaction has begun, publish a non-auto-dismissing `Snack` with severity `'info'`, `duration: Infinity`, and an action `{ label: '更新', callback: updateSW }`. When the user taps [更新], `updateSW(true)` is called (SKIP_WAITING → SW activates → `virtual:pwa-register`'s internal `controlling` handler reloads the page once). Boot-time exception: if `onNeedRefresh` fires before the first `pointerdown`/`touchstart` event, apply silently (no toast, no user action required).

**Prerequisite:** `snack-bar.ts` must guard `if (durationMs === Infinity)` before setting the auto-dismiss `setTimeout`. Without this guard, `setTimeout(fn, Infinity)` coerces to `setTimeout(fn, 0)` (ToInt32 overflow → 0) and the toast auto-dismisses on the next tick.

**Rationale:** The existing `Snack` component already supports `action` and `duration` options — no new component needed. Non-blocking toast matches Material/web.dev best practices. The boot-time exception covers the case where the app was just opened and the old SW was already waiting; there is no in-progress work to interrupt.

**Alternative considered:** Reload silently on "safe routes" (no form input). Rejected: "safe" is hard to define correctly, and reload during any active reading/scrolling session causes unnecessary surprise per UX review in exploration.

### D3 — Build SHA injected at build time via vite `define`

**Decision:** Add `define: { __BUILD_SHA__: JSON.stringify(process.env.GITHUB_SHA?.slice(0, 7) ?? 'dev') }` to `vite.config.ts`. The 7-character prefix is sufficient for disambiguation and matches the convention used in GitHub URLs.

**Rationale:** The SHA identifies the exact code artifact independently of the release label. It is the most reliable fingerprint for debugging (unlike `releaseVersion` which is added post-retag). It is available at `npm run build` time via `GITHUB_SHA` in CI; local dev falls back to the literal string `'dev'`.

**Alternative considered:** Use `package.json` version as the build-time identifier. Rejected: `package.json` version is `0.1.0` (a placeholder, not bumped per release); the git SHA is the true build identity.

### D4 — `releaseVersion` carried in config.json, written by pin-bump workflow

**Decision:** Add an optional `releaseVersion?: string` field to the `AppConfig` TypeScript interface and to all per-environment config.json ConfigMaps in cloud-provisioning. The prod pin-bump workflow writes `"releaseVersion": "vX.Y.Z"` (including the `v` prefix, matching the git tag format). The dev ConfigMap receives `"releaseVersion": "dev"` as a static placeholder.

**Rationale:** The retag-based release pipeline means the semver tag is only known at release time, after the image is already built. config.json is the correct place: it is per-environment, served NetworkOnly (always fresh), and already touched by the pin-bump workflow on every release. The field is optional (frontend renders gracefully when absent, e.g., during the rollout window before cloud-provisioning catches up).

**Alternative considered:** Bake the version into the bundle via `vite define`. Rejected: the build runs before the release tag exists (retag architecture), so `RELEASE_VERSION` would be empty or wrong at build time.

### D5 — Settings version row: display only, copy-to-clipboard for support

**Decision:** Add a read-only row to the Settings screen ("アプリ情報" section, placed last) showing the release version from `AppConfig.releaseVersion` and the build SHA from `__BUILD_SHA__`. Tapping the row copies the combined string (`v1.26.0 (abc1234)`) to the clipboard. No navigation. Authenticated and guest users both see it.

**Rationale:** A copy-to-clipboard affordance directly addresses the support use-case (bug report context) without requiring a dedicated detail page. "アプリ情報" as the section title is familiar iOS/Android convention.

### D6 — `update()` triggered on boot and visibilitychange

**Decision:** Pass an `onRegisteredSW` callback to `registerSW` that sets up a periodic `registration.update()` on `visibilitychange:visible` (reusing the pattern already established by `ResumeRevalidator`). No additional interval timer — visibilitychange-driven polling is sufficient for the always-on PWA use case.

**Rationale:** Without explicit `update()` calls, the browser defers the SW check by up to 24 hours. Installed PWAs that are never fully quit would then go a full day before receiving updates. Piggybacking on `visibilitychange` keeps the update check free and avoids a polling timer.

## Risks / Trade-offs

- **[Risk] `clients.claim()` in activate takes control of already-open pages instantly.** A page loaded under the old SW and then `claim()`ed by the new SW could mix old HTML routes with new precache, causing a brief inconsistency window. → **Mitigation:** `clients.claim()` is safe here because we only reach activate after the user explicitly tapped [更新] (or the boot-time silent path, where no page state exists yet). The controllerchange listener reloads immediately, so the inconsistency window is sub-second.
- **[Risk] `duration: Infinity` Snacks accumulate if update events fire repeatedly.** → **Mitigation:** Store the `SnackHandle` returned after the EA publish. A non-null handle means a toast is already showing; on a second `onNeedRefresh`, call `handle.dismiss()` before publishing the replacement. Do NOT add a separate boolean flag — the handle itself is the authoritative state (a separate flag can drift if the snack-bar dismisses the toast externally).
- **[Risk] config.json `releaseVersion` lags during the pin-bump rollout window.** Between a GH Release being created and the cloud-provisioning PR merging + ArgoCD syncing, the running pods still serve the old config.json (without or with stale `releaseVersion`). → **Mitigation:** The field is optional in TypeScript; the Settings row renders `—` or omits the version when absent, without error.
- **[Risk] `GITHUB_SHA` is not set in local dev builds.** → **Mitigation:** The `vite define` expression falls back to the literal string `'dev'`, which is a clear and harmless placeholder.

## Migration Plan

1. **frontend PR first:** Add `__BUILD_SHA__` define, switch to `registerSW`, add SW-side SKIP_WAITING + clients.claim, add Settings version row reading `config?.releaseVersion ?? '—'`. The field is optional so frontend ships without waiting for CP.
2. **cloud-provisioning PR:** Add `releaseVersion` to dev and prod config.json ConfigMaps, update pin-bump workflow to write the field on each release.
3. **No rollback complexity:** The config.json change is additive; removing `releaseVersion` later is safe (frontend already handles absence). The SW changes are isolated to registration and SW internals with no protocol changes.

## Open Questions

- The update Snack message copy ("新しいバージョンが利用可能です") and the [更新] button label need i18n keys — confirm with the standard `settings.*` or `common.*` namespace convention used elsewhere.
- Should the build SHA row be visible only in dev/staging, or in prod too? (Current design: always visible — useful for prod bug reports. Revisit if product decides it is noise for end users.)
