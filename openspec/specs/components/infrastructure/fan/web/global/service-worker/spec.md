# Service Worker

## Purpose

Runs the app's background service process, which registers on boot, checks for and applies updates silently before user interaction, renews the push subscription when it changes, and bounds all its network calls to a time limit.

## Requirements

### Requirement: Service-Worker analytics capture is time-bounded

The Service-Worker `fetch()` that delivers a notification-interaction event to the analytics endpoint SHALL be bounded by a timeout, so that a slow (not failed) response is converted into an abort and routed through the existing offline-resend path rather than being lost or holding the Service Worker active.

#### Scenario: A slow analytics capture is stashed for resend

- **WHEN** the analytics capture `fetch()` does not complete within its timeout
- **THEN** the fetch SHALL be aborted
- **AND** the interaction SHALL be treated as a failed send and stashed for retry via the existing Background-Sync / app-open resend path
- **AND** the same de-duplication identifier SHALL be reused so the eventual resend is not double-counted

### Requirement: Service-Worker VAPID key fetch is time-bounded

The Service-Worker cache-miss `fetch()` that reads the VAPID public key from `/config.json` during push-subscription renewal SHALL be bounded by a timeout, so that a `pushsubscriptionchange` handler cannot hang on a stalled network fetch.

#### Scenario: A stalled VAPID fetch does not hang renewal

- **WHEN** the VAPID key is not present in the cache and the network `fetch()` for `/config.json` does not complete within its timeout
- **THEN** the fetch SHALL be aborted
- **AND** the renewal SHALL treat the key as unavailable and skip renewal without throwing
- **AND** the existing app-open reconciliation path SHALL remain able to recover the subscription on next app launch

This scenario bounds only the VAPID-key `fetch()`; it does not change how the Service Worker treats an existing or stale subscription endpoint (that behavior remains governed by the `push-notification-service` capability).

### Requirement: Service Worker renews the subscription on pushsubscriptionchange

The Service Worker SHALL handle the `pushsubscriptionchange` event. When the push service rotates or expires the subscription, the Service Worker SHALL obtain a new subscription using the configured VAPID application server key, without any user interaction and without the app UI being open, and SHALL tell any open app window that the subscription changed. The Service Worker cannot act for the signed-in fan, so the new subscription SHALL be registered with the server by an open app window at once, or otherwise the next time the app opens (see the app shell), so that browser-initiated subscription churn does not silently end delivery.

#### Scenario: Browser rotates the subscription

- **WHEN** the browser fires `pushsubscriptionchange` in the Service Worker
- **AND** a new subscription can be obtained with the configured VAPID application server key
- **THEN** the Service Worker SHALL subscribe to the push service for the new subscription
- **AND** the new subscription SHALL be registered with the server by an open app window, or when the app next opens
- **AND** the user SHALL continue to receive push notifications without re-enabling them

#### Scenario: Renewal cannot obtain a new subscription

- **WHEN** the Service Worker handles `pushsubscriptionchange`
- **AND** a new subscription cannot be obtained (e.g., permission was revoked)
- **THEN** the Service Worker SHALL NOT crash the event
- **AND** the stale endpoint SHALL NOT remain registered as if active

### Requirement: The app registers its service worker via the platform's PWA registration mechanism

The app SHALL register its service worker through the PWA registration mechanism provided by the build tooling, configured to prompt the user before applying updates (`registerType: 'prompt'`), rather than using a direct low-level registration call. The registration SHALL be invoked at application startup and SHALL be skipped outside production environments.

#### Scenario: Service worker is registered via the PWA registration mechanism in production

- **WHEN** the app loads in a production environment
- **THEN** the service worker SHALL be registered through the PWA registration mechanism
- **AND** a direct low-level registration call SHALL NOT exist in the entry point

#### Scenario: Service worker registration is skipped in dev mode

- **WHEN** the app loads under the development server
- **THEN** the service worker registration SHALL NOT be invoked
- **AND** no service worker SHALL be registered

### Requirement: The Service Worker SHALL handle `SKIP_WAITING` messages and claim clients on activate

The Service Worker SHALL listen for `{type: 'SKIP_WAITING'}` messages and invoke `self.skipWaiting()` in response. On the `activate` event, the SW SHALL invoke `self.clients.claim()` so that pages loaded under the previous SW controller are immediately transferred to the new SW after a reload.

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

### Requirement: The SPA applies a waiting SW silently on boot before user interaction

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

### Requirement: The SPA triggers SW update checks on boot and on page resume

The SPA SHALL call `registration.update()` on SW registration completion and on every `visibilitychange` event where `document.visibilityState === 'visible'`. This ensures that installed PWA users who never fully quit the app receive SW updates promptly rather than waiting up to 24 hours for the browser's default check interval.

#### Scenario: Update check on registration

- **WHEN** `registerSW` calls the `onRegisteredSW` callback with the SW URL and a non-undefined registration
- **THEN** `registration.update()` SHALL be called once immediately
- **AND** when `onRegisteredSW` is called with `registration === undefined` (SW registration failed), the callback SHALL return without calling `update()` — a `TypeError` on `undefined.update()` SHALL NOT be thrown

#### Scenario: Update check on resume

- **WHEN** `document.visibilityState` transitions to `'visible'`
- **THEN** `registration.update()` SHALL be called
- **AND** if a new SW is found, `updatefound` → `statechange` → `onNeedRefresh` SHALL fire normally
