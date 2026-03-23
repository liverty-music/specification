## Why

The post-signup onboarding flow has three UX issues that together degrade first-run experience:

1. **Language switcher inaccessible before sign-up.** The only language toggle lives in Settings, which requires authentication. Users whose browser locale doesn't match their preferred language have no way to switch before completing onboarding.

2. **Coach mark tooltip has opaque background on dark overlay.** The spotlight darkens the viewport to 70% black, but the tooltip uses a solid `--color-surface-overlay` fill. This creates visual weight redundancy — two dark layers stacked — making the tooltip feel heavy and disconnected from the spotlight rather than floating naturally on the overlay.

3. **Bottom sheet invisible when `dismissable=false` (progression blocker).** After the celebration overlay completes on the Dashboard, the User Home Selector bottom sheet opens but its content is not visible. The user sees a dark screen with no interactive elements. Root cause: CSS selector `:not([data-dismissable])` checks for attribute *absence*, but Aurelia outputs `data-dismissable="false"` (attribute *present* with string value), so the dismiss-zone's scroll-snap is never disabled — the browser snaps to the empty dismiss-zone instead of the sheet body.

## What Changes

- **Frontend (welcome-route)**: Add a language toggle below the CTA buttons. Extract the language switching logic from Settings into a reusable utility.
- **Frontend (coach-mark)**: Remove the tooltip's solid background and drop-shadow. The handwritten font (`Klee One`) text renders directly on the dark overlay.
- **Frontend (bottom-sheet)**: Fix the CSS selector to match Aurelia's boolean attribute output. Change from `:not([data-dismissable])` to `:not([data-dismissable="true"])` so dismiss-zone snap is correctly disabled when `dismissable=false`.
- **Specification (bottom-sheet-ce)**: Update spec to reflect the current architecture (popover on CE host, scroll-area separation) and the dismiss-zone CSS-controlled snap behavior.

## Capabilities

### New Capabilities

- `landing-page`: Language switcher on the Welcome page for unauthenticated users.

### Modified Capabilities

- `bottom-sheet-ce`: DOM structure updated to reflect CE host popover architecture; non-dismissable scenario updated to describe CSS-controlled dismiss-zone snap (always in DOM, snap disabled via CSS attribute selector).
- `onboarding-spotlight`: Tooltip visual treatment changed from solid background to transparent.
- `frontend-i18n`: Language switching extracted to a shared utility; available on Welcome page in addition to Settings.

## Impact

- **frontend only** — no backend, proto, or infrastructure changes required.
- **No breaking changes** — all changes are visual/behavioral fixes within existing components.
- The bottom-sheet fix affects all consumers using `dismissable.bind="false"` (user-home-selector, tickets-route, error-banner).
