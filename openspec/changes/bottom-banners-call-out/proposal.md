## Why

Signing up and installing the app are close to preconditions for using the service, so the two bottom banners that ask for them (the signup prompt and the install banner) should be hard to miss. Today they get in their own way and in the content's:

- While a banner is visible, the FAB floats above it (a stopgap from `unify-fan-buttons-and-center-fab`) and covers the content there, such as My Artists' empty-state button.
- The banner covers the end of every route's scroll area, so the last row cannot be tapped (frontend#787: Settings' Sign out).
- The banners' button uses the `on-container` style, meant for coloured surfaces. On the banners' dark surface it reads as a grey button.
- The install banner truncates its message with an ellipsis, and it can be closed for the tab, which survives reloads although the spec says a page load brings it back.
- The CTA glows three times when the banner appears and then never again.

The user compared preview options and chose to keep both banners always visible, out of the FAB's way like a snack bar, with a recurring attention cue.

## What Changes

- **FAB.** While a bottom banner is visible, the FAB sinks into the navigation bar exactly as it does under a snack bar. It no longer floats above the banner. **BREAKING** for the stopgap behaviour.
- **Layout.** Both banners show one row: the message, then the CTA. They have no icon and no close button. The message and the CTA label share one text size that follows the banner's width, so both fit on one line at every phone width, without truncation, in Japanese and English.
- **CTA.** The CTA uses the filled (brand-primary) button at the compact size of the snack bar's action. `on-container` stays for buttons on coloured surfaces (the snack bar).
- **Attention cue.** Every 12 seconds while a banner is visible, a light runs along its top brand line and then across the CTA. The cue plays at most 5 times per route visit, and never with reduced motion. Nothing moves or changes size, so the CTA never changes under a finger.
- **Copy.** The signup prompt reads 「フォロー履歴を保存しよう！」 with a 「Sign Up」 button. The install banner reads 「新着ライブ通知を受け取ろう！」 with 「Install」. The English copy is "Save your follows!" and "Get new show alerts!", with "Sign Up" and "Install".
- **No dismiss.** The install banner's close button and its per-tab dismiss are removed. The banner stays until the app is installed or the fan confirms the install in the guide sheet. **BREAKING** for the spec's session-level dismiss.
- **Content clears the banner.** While a banner is visible, the route area ends at the banner's top edge, so the last row of every scrolled route can be scrolled above it and an empty state is centred in the area the fan can see (frontend#787).

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `components/infrastructure/fan/web/global/pwa-install-banner`: the presentation (one row, filled compact CTA, fitted text, no icon or close, attention cue), its accessibility and its i18n. "Session-Level Dismiss" is removed, and the visibility requirements drop the session-dismiss flag.
- `components/infrastructure/fan/web/global/signup-prompt-banner`: the copy, and the shared presentation and attention cue.
- `components/infrastructure/fan/web/global/fab-menu`: the FAB sinks under a bottom banner as under a snack bar, and no longer floats above it.
- `components/infrastructure/fan/web/global/bottom-nav-bar`: the notch stays cut while the FAB is sunk under a banner.
- `components/infrastructure/fan/web/global/snack-bar`: a snack bar sits above a visible banner with the FAB sunk, and no longer above a floating FAB.
- `components/infrastructure/fan/web/global/ui-primitives`: the filled compact button on a bottom banner; `on-container` is for coloured surfaces only.
- `components/infrastructure/fan/web/global/notification-prompt`: the install banner's session-dismiss scenarios are removed.
- `components/infrastructure/fan/web/global/app-shell`: the route area ends above a visible bottom banner.

## Impact

- **frontend only.** No proto, backend or infrastructure change.
- `src/components/pwa-install-banner/` and `src/components/signup-prompt-banner/` (templates, CSS, view models, stories), `src/styles/global.css`, `src/components/fab-menu/fab-menu.css`, `src/components/bottom-nav-bar/`, `shared/ui/snack-bar/snack-bar.css`, `src/app-shell.css`.
- `src/locales/{ja,en}/translation.json` and `src/constants/storage-keys.ts` (the dismiss key goes).
- E2E: `e2e/functional/snack-bar.spec.ts` and `e2e/functional/fab-menu-arc.spec.ts` (banner placement), and a new check that the last row and the empty state clear the banner.
- frontend#787 is closed by this change.
