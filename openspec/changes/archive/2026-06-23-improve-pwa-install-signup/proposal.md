## Why

The PWA install button in the PostSignupDialog intermittently fails to appear after sign-up because `PwaInstallService` is constructed too late to capture the browser's `beforeinstallprompt` event, and the current design entirely hides the install row when the event hasn't been received — leaving users with no install path even when their browser fully supports it.

## What Changes

- `PwaInstallService` gains two new public getters (`browserSupportsPwa`, `canShowInstallOption`) that expose install capability independently of whether `beforeinstallprompt` has fired yet
- `AppShell` eagerly resolves `PwaInstallService` on activation to register the `beforeinstallprompt` listener before any routing occurs (fixing the timing race)
- `PostSignupDialog` changes its install-row condition from `canShowFab` (requires captured prompt) to `canShowInstallOption` (requires only browser support), showing a native `<details>`/`<summary>` "How to add" instruction disclosure when the native prompt is unavailable
- `PostSignupDialog` adds an explicit `@watch` on `canShowFab` to ensure reliable reactivity when the native prompt arrives after the dialog opens
- Translation keys added for the Chrome/Edge install instruction steps

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `post-signup-dialog`: PWA install row condition changes from requiring a captured `beforeinstallprompt` event to requiring only that the browser supports the PWA install API; row shows native prompt or manual instructions depending on availability.

## Impact

- **Frontend only** — no backend, proto, or cloud-provisioning changes
- `src/services/pwa-install-service.ts` — two new public getters
- `src/app-shell.ts` — one new DI resolve for eager construction
- `src/components/post-signup-dialog/post-signup-dialog.ts` — condition and watcher changes
- `src/components/post-signup-dialog/post-signup-dialog.html` — native install button vs. `<details>` install-guide disclosure
- `src/components/post-signup-dialog/post-signup-dialog.css` — `.post-signup-install-steps` list + `.post-signup-install-guide summary` styling
- `src/locales/ja/translation.json`, `src/locales/en/translation.json` — new `postSignup.pwaInstallGuide`, `postSignup.pwaGuideStep1-3` keys
- Existing `pwa-install-fab` behavior is unchanged; `PwaInstallService.canShowFab` semantics are preserved for the FAB
