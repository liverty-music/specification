## 1. Service Worker: SKIP_WAITING + clients.claim (frontend)

- [ ] 1.1 Add `{type: 'SKIP_WAITING'}` message handler to `src/sw.ts` that calls `self.skipWaiting()`
- [ ] 1.2 Combine `self.clients.claim()` with the existing `flushInteractionStash()` call in the `activate` handler: `event.waitUntil(Promise.all([self.clients.claim(), flushInteractionStash()]))` — do NOT replace the existing `waitUntil` call, as dropping `flushInteractionStash()` silently loses offline-stashed notification interaction analytics
- [ ] 1.3 Verify `make check` passes (TypeScript + unit tests)

## 2. Build SHA injection (frontend)

- [ ] 2.1 Add `define: { __BUILD_SHA__: JSON.stringify(process.env.GITHUB_SHA?.slice(0, 7) ?? 'dev') }` to `vite.config.ts`
- [ ] 2.2 Add `declare const __BUILD_SHA__: string` to `src/vite-env.d.ts` (or equivalent global types file) so TypeScript resolves the constant

## 3. SW registration: switch to `virtual:pwa-register` (frontend)

- [ ] 3.1 Remove the bare `navigator.serviceWorker.register('/sw.js')` block from `src/main.ts`
- [ ] 3.2 Import `registerSW` from `virtual:pwa-register` in `src/main.ts`
- [ ] 3.3 Set `registerType: 'prompt'` in the `VitePWA({})` options in `vite.config.ts` (document: this sets the virtual module's behaviour, not the manifest)
- [ ] 3.4 Implement boot-time interaction tracking: attach a one-time `pointerdown`/`touchstart` listener on `window` to set a `hasInteracted` flag
- [ ] 3.5 Implement `onNeedRefresh` callback: if `!hasInteracted`, call `updateSW(true)` silently; otherwise publish the update Snack
- [ ] 3.6 Implement `onRegisteredSW` callback: guard against `undefined` registration (`if (!registration) return`), then call `registration.update()` immediately, and add a `visibilitychange` listener that calls `registration.update()` when `document.visibilityState === 'visible'`

## 4. Update toast (frontend)

- [ ] 4.1 Add a persistent-duration guard to `src/components/snack-bar/snack-bar.ts`: before calling `setTimeout(dismiss, event.durationMs)`, skip the timer entirely when `event.durationMs === Infinity` — without this guard, `setTimeout(fn, Infinity)` coerces to `setTimeout(fn, 0)` (ToInt32 overflow) and the toast auto-dismisses immediately
- [ ] 4.2 Add i18n keys `pwa.updateAvailable` and `pwa.updateAction` to the English and Japanese translation files
- [ ] 4.3 Implement the update Snack publication in `onNeedRefresh`: `new Snack(i18n.tr('pwa.updateAvailable'), 'info', { duration: Infinity, action: { label: i18n.tr('pwa.updateAction'), callback: () => updateSW(true) } })`
- [ ] 4.4 Track the active update Snack via its `SnackHandle` (store the `snack.handle` value returned after EA publish) — if `onNeedRefresh` fires again while a handle is non-null, call `handle.dismiss()` before publishing the replacement; do NOT add a separate boolean flag alongside the handle (handle non-null ≡ toast is showing)

## 5. AppConfig: `releaseVersion` field (frontend + cloud-provisioning)

- [ ] 5.1 Add `readonly releaseVersion?: string` to the `AppConfig` interface in `shared/config/app-config.ts`
- [ ] 5.2 Confirm `validateAppConfig` in `app-config.ts` treats `releaseVersion` as optional (no validation failure when absent)
- [ ] 5.3 Add `"releaseVersion": "dev"` to `frontend/public/config.json` (dev fallback)
- [ ] 5.4 Add `"releaseVersion": "dev"` to the dev ConfigMap in `cloud-provisioning/k8s/namespaces/frontend/overlays/dev/configmap.yaml`
- [ ] 5.5 Add `"releaseVersion": "v<current-tag>"` to the prod ConfigMap in `cloud-provisioning/k8s/namespaces/frontend/overlays/prod/configmap.yaml` (use the current prod tag, e.g. `v1.26.0`)

## 6. Pin-bump workflow: write `releaseVersion` to configmap (cloud-provisioning)

- [ ] 6.1 In `bump-prod-pin.yml`, after the `kustomization.yaml` rewrite step for `component=frontend`, add a `yq -i` (or `jq` + `sed`) step that writes the tag value into the `releaseVersion` field inside the `config.json` JSON blob in `k8s/namespaces/frontend/overlays/prod/configmap.yaml`
- [ ] 6.2 Verify the no-downgrade guard executes before the ConfigMap write step so a blocked pin-bump leaves configmap.yaml untouched
- [ ] 6.3 Confirm the PR created by the workflow includes both the `kustomization.yaml` and `configmap.yaml` changes in the same commit

## 7. Settings: app version display (frontend)

- [ ] 7.1 Add an "アプリ情報" section to `src/routes/settings/settings-route.html` at the bottom of the `<main>` scroll area
- [ ] 7.2 Add `releaseVersion` and `buildSha` getters to `SettingsRoute` in `settings-route.ts`: `releaseVersion` reads `IAppConfig.releaseVersion ?? '—'`; `buildSha` reads `__BUILD_SHA__`
- [ ] 7.3 Implement the copy-to-clipboard handler: `navigator.clipboard.writeText(`${this.releaseVersion} (${this.buildSha})`)` on row tap
- [ ] 7.4 Add i18n key `settings.appInfo` (section title) and `settings.copyVersionSuccess` (optional success feedback)
- [ ] 7.5 Add accessible label for the version row (e.g., `aria-label` combining version + copy affordance hint)

## 8. Verification

- [ ] 8.1 Run `make check` in `frontend` repo — TypeScript compilation, unit tests, and build-template verification all pass
- [ ] 8.2 Manually install the PWA (Chrome + Android or desktop), deploy a new version, and confirm: (a) the update toast appears, (b) tapping [更新] reloads to the new version, (c) Settings shows the updated `releaseVersion`
- [ ] 8.3 Verify boot-time silent apply: open a fresh browser tab to the app while a waiting SW exists — confirm reload happens without a toast
- [ ] 8.4 Confirm no double-reload (reloop) occurs by opening two tabs and applying the update from one
- [ ] 8.5 After a frontend release and cloud-provisioning pin-bump PR merges, confirm the prod `config.json` served at `https://liverty-music.app/config.json` contains the correct `releaseVersion`
- [ ] 8.6 Ship to prod (frontend release + cloud-provisioning pin-bump) and verify in Settings
