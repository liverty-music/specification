# PWA Update Lifecycle

## Purpose

Defines the Service Worker registration and update lifecycle for the Aurelia 2 frontend PWA. This capability specifies how the SPA registers its SW via `vite-plugin-pwa`, detects available updates, applies them silently on boot (pre-interaction) or presents a user-confirmable toast (post-interaction), and ensures that installed-PWA users receive SW updates promptly rather than waiting up to 24 hours for the browser's default check interval.

## Requirements

### Requirement: The SPA SHALL register its Service Worker via `virtual:pwa-register`

The SPA SHALL use the `registerSW` function from `virtual:pwa-register` (provided by `vite-plugin-pwa`) in place of the bare `navigator.serviceWorker.register()` call. The `registerType` configuration SHALL be set to `'prompt'`. The registration SHALL be invoked in the SPA bootstrap entry point and SHALL be guarded against non-production environments (`import.meta.env.DEV`).

#### Scenario: SW is registered via virtual module in production

- **WHEN** the SPA loads in a browser where `import.meta.env.DEV` is `false`
- **THEN** `registerSW` from `virtual:pwa-register` SHALL be invoked
- **AND** the bare `navigator.serviceWorker.register('/sw.js')` call SHALL NOT exist in the entry point

#### Scenario: SW registration is skipped in dev mode

- **WHEN** the SPA loads under the Vite dev server (`import.meta.env.DEV === true`)
- **THEN** `registerSW` SHALL NOT be called
- **AND** no service worker SHALL be registered

### Requirement: The Service Worker SHALL handle `SKIP_WAITING` messages and claim clients on activate

The Service Worker (`sw.ts`) SHALL listen for `{type: 'SKIP_WAITING'}` messages and invoke `self.skipWaiting()` in response. On the `activate` event, the SW SHALL invoke `self.clients.claim()` so that pages loaded under the previous SW controller are immediately transferred to the new SW after a reload.

#### Scenario: SW activates on SKIP_WAITING message

- **WHEN** the SW is in the `installed` (waiting) state
- **AND** the page sends `{type: 'SKIP_WAITING'}` via `postMessage`
- **THEN** the SW SHALL call `self.skipWaiting()`
- **AND** the SW SHALL transition to `activating` then `activated` without requiring all tabs to close

#### Scenario: SW claims open clients on activate

- **WHEN** the SW transitions to `activated`
- **THEN** `self.clients.claim()` SHALL be called within `event.waitUntil()` combined with the existing `flushInteractionStash()` call — specifically `event.waitUntil(Promise.all([self.clients.claim(), flushInteractionStash()]))`
- **AND** any page previously controlled by the outgoing SW SHALL be transferred to the new SW
- **AND** the existing `flushInteractionStash()` call SHALL NOT be removed or replaced (dropping it silently loses offline-stashed notification interaction analytics)

### Requirement: The SPA SHALL show a persistent update toast when a waiting SW is detected after user interaction

When `vite-plugin-pwa` detects a waiting SW (`onNeedRefresh` callback) after the user has begun interacting with the page, the SPA SHALL publish a non-auto-dismissing `Snack` notification with an action button that, when tapped, sends `SKIP_WAITING` to the waiting SW, triggering a `controllerchange` event and a single-shot page reload.

#### Scenario: Update toast shown after user interaction

- **WHEN** a new Service Worker reaches the `installed` (waiting) state
- **AND** the user has already performed at least one pointer or keyboard interaction with the page
- **THEN** the SPA SHALL publish a `Snack` event via `IEventAggregator` with:
  - severity: `info`
  - `duration: Infinity` (no auto-dismiss)
  - an `action` button labelled with the i18n key `pwa.updateAction`
- **AND** at most one update `Snack` SHALL be active at a time

#### Scenario: Tapping the update action triggers reload

- **WHEN** the user taps the [更新] action on the update Snack
- **THEN** `updateSW(true)` SHALL be called (dispatches `SKIP_WAITING` to the waiting SW)
- **AND** the page SHALL reload exactly once via `controllerchange`
- **AND** after reload the page SHALL be controlled by the new Service Worker

#### Scenario: No duplicate reloads (reloop guard)

- **WHEN** `controllerchange` fires
- **THEN** `location.reload()` SHALL be called at most once per lifecycle
- **AND** a subsequent `controllerchange` event (e.g., from another tab's skipWaiting) SHALL NOT trigger a second reload on the same page

### Requirement: The SPA SHALL apply a waiting SW silently on boot before user interaction

If a waiting SW is detected (`onNeedRefresh`) before the user's first `pointerdown` or `touchstart` event (i.e., the app just started and has not yet received any interaction), the SPA SHALL apply the update silently — without showing a toast — by immediately calling `updateSW(true)`, then reloading via `controllerchange`.

#### Scenario: Silent apply on first load with a waiting SW

- **WHEN** `onNeedRefresh` fires during the boot sequence
- **AND** no `pointerdown` or `touchstart` event has been recorded on `window` yet
- **THEN** `updateSW(true)` SHALL be called immediately (no toast)
- **AND** the page SHALL reload once after `controllerchange`

#### Scenario: Toast shown when update detected after interaction has begun

- **WHEN** `onNeedRefresh` fires
- **AND** at least one `pointerdown` or `touchstart` event has already been recorded
- **THEN** the SPA SHALL show the update toast (per "Update toast shown after user interaction" above)
- **AND** SHALL NOT reload without user confirmation

### Requirement: The SPA SHALL trigger SW update checks on boot and on page resume

The SPA SHALL call `registration.update()` on SW registration completion and on every `visibilitychange` event where `document.visibilityState === 'visible'`. This ensures that installed PWA users who never fully quit the app receive SW updates promptly rather than waiting up to 24 hours for the browser's default check interval.

#### Scenario: Update check on registration

- **WHEN** `registerSW` calls the `onRegisteredSW` callback with the SW URL and a non-undefined registration
- **THEN** `registration.update()` SHALL be called once immediately
- **AND** when `onRegisteredSW` is called with `registration === undefined` (SW registration failed), the callback SHALL return without calling `update()` — a `TypeError` on `undefined.update()` SHALL NOT be thrown

#### Scenario: Update check on resume

- **WHEN** `document.visibilityState` transitions to `'visible'`
- **THEN** `registration.update()` SHALL be called
- **AND** if a new SW is found, `updatefound` → `statechange` → `onNeedRefresh` SHALL fire normally
