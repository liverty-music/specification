<!-- spec: pwa-update-lifecycle | target: components/infrastructure/fan/web/service-worker | flags: CLASSNAME | new_name: The Service Worker handles SKIP_WAITING messages and claims clients on activate -->
<!-- implementation names to remove: sw.ts -->

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
