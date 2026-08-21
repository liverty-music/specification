## Why

The PWA install FAB is insufficiently prominent — a 2.75 rem circular button in the screen corner that is easy to overlook. Because push notifications (the core feature of this service) require PWA installation on iOS 16.4+, low install conversion directly limits reach. A persistent banner using the same visual language as the proven `signup-prompt-banner` raises the install CTA to a prominence level appropriate for a core-feature dependency.

## What Changes

- **New**: `pwa-install-banner` component — full-width persistent fixed banner shown to signed-in, non-installed users. Reuses `signup-prompt-banner` visual treatment (gradient border-top, frosted glass, pulsing CTA). Supports two CTA modes: native one-tap install (Chrome/Edge with deferred prompt) and guided manual steps (iOS Safari / no deferred prompt).
- **New**: `PwaInstallService.shouldShowInstallBanner` `@observable` property — visibility predicate for the banner. Extends eligibility to iOS Safari (`!installed && (browserSupportsPwa || isIos)`), unlike the existing `canShowInstallOption` which excludes iOS.
- **New**: `PwaInstallService.confirmInstalled()` — allows iOS users to manually confirm installation from the guide sheet, compensating for unreliable `appinstalled` event on iOS.
- **New**: Session-level dismiss — the banner can be dismissed per session via a close button; the dismiss state is stored in `sessionStorage` and clears on next session load, so the banner reappears until the app is installed.
- **REMOVED**: `pwa-install-fab` component (all files: `.ts`, `.html`, `.css`, `.spec.ts`).
- **Modified**: `PwaInstallService` — adds `shouldShowInstallBanner` and `confirmInstalled()`; existing `canShowFab`, `canShowInstallOption`, `isIos`, and `browserSupportsPwa` are unchanged.
- **Modified**: `app-shell.html` / `app-shell.ts` — swap `<pwa-install-fab>` for `<pwa-install-banner>`.
- **Modified**: `prompt-timing` spec — update "PWA install FAB has no dismiss action" rule to reflect session-level dismiss; clarify that session dismiss is not a permanent suppression.
- **Modified**: `post-signup-dialog` spec — update iOS install path reference from "persistent FAB" to `pwa-install-banner`.

## Capabilities

### New Capabilities

- `pwa-install-banner`: Persistent PWA install promotion banner for signed-in users, with session-level dismiss, iOS support (guided sheet), and reactive CTA mode switching (native vs. guide).

### Modified Capabilities

- `pwa-install-fab`: All requirements REMOVED — capability retired and superseded by `pwa-install-banner`.
- `prompt-timing`: Update "passive UI / no dismiss" language to reflect banner's session-level dismiss while preserving the banner's classification as passive (not subject to the single-prompt-per-session constraint).
- `post-signup-dialog`: Update iOS install path reference from FAB instruction sheet to `pwa-install-banner`.

## Impact

- **Frontend only** — no backend, proto, or BSR changes required.
- **New component**: `src/components/pwa-install-banner/` (`.ts`, `.html`, `.css`)
- **Deleted component**: `src/components/pwa-install-fab/` (all files)
- **Service change**: `src/services/pwa-install-service.ts` (additive only)
- **Shell change**: `src/app-shell.html`, `src/app-shell.ts`
- **i18n**: New translation keys (`pwaInstallBanner.*`) in `en/translation.json` and `ja/translation.json`
