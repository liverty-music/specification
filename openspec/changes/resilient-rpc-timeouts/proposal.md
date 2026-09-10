## Why

Connect-RPC calls from the frontend currently have **no client-side timeout** (neither `defaultTimeoutMs` on the transport nor per-call `timeoutMs`). A hung or wedged backend leaves the user staring at a spinner indefinitely — a silent failure with no upper bound. Two Service-Worker `fetch()` calls (PostHog analytics capture, cache-miss VAPID key read) are likewise unbounded, so a slow-but-not-failed response neither succeeds nor falls into the existing retry/stash path.

Investigation of the full request path (browser → Cloudflare DNS-only → GCP ALB → `http.TimeoutHandler` → downstream) established that every RPC the frontend actually invokes is a fast unary read/mutation (sub-second in practice); the only legitimately long backend operation (120 s Gemini `SearchNewConcerts`) is **not called from any frontend app**. A single, short client-side deadline is therefore both safe and sufficient.

## What Changes

- Introduce a single **client-side default RPC timeout of 10 s** on the shared Connect transport (`defaultTimeoutMs`), applied uniformly across all three frontend apps (fan-web, admin, organizer). No per-method overrides are needed because no frontend call is legitimately long-running.
- Make the timeout value **runtime-configurable via `/config.json`** (optional field, defaulting to 10 s when absent), mirroring the backend's env-configurable timeout convention and allowing per-environment tuning without a rebuild.
- Add `AbortSignal.timeout(...)` to the two unbounded Service-Worker `fetch()` calls:
  - PostHog analytics capture (`sendInteraction`) — bounded so a slow response is turned into an `AbortError` and routed through the existing stash → Background-Sync resend path instead of being lost.
  - Cache-miss VAPID key read (`readVapidPublicKeyCacheFirst`) — bounded so a `pushsubscriptionchange` handler cannot hang on a stalled network fetch.
- Leave the existing 5 s `/config.json` bootstrap-fetch timeout and Connect's internal abort-signal composition unchanged (no `AbortSignal.any` hand-rolling required).

No breaking changes. All modifications are additive resilience behavior within the `frontend/` repository.

## Capabilities

### New Capabilities
- `frontend-network-timeouts`: Client-side network timeout policy for the Aurelia 2 frontend — the default Connect-RPC call deadline (its value, source, and uniform application across apps) and bounded Service-Worker `fetch()` calls, so that no browser-originated network request can hang without an upper bound.

### Modified Capabilities
<!-- None. The new `/config.json` field is additive and does not change any existing
     frontend-runtime-config scenario (its scenarios assert specific fields exist and
     that no VITE_ values leak — an added optional field violates neither). -->

## Impact

- **Repository**: `frontend/` only.
- **Code**:
  - `src/services/grpc-transport.ts` — set `defaultTimeoutMs` on `createConnectTransport`, sourced from `AppConfig`.
  - `shared/config/app-config.ts` — add optional `rpcTimeoutMs` to the config type + validation, defaulting to 10 s.
  - `config.json` (and per-environment ConfigMaps under `cloud-provisioning`) — optional additive field.
  - `src/lib/analytics/notification-interaction.ts` — bound `sendInteraction` fetch.
  - `src/lib/push/push-renewal.ts` — bound `readVapidPublicKeyCacheFirst` cache-miss fetch.
- **Behavior**: RPC calls now reject with `Code.DeadlineExceeded` after 10 s (already NOT retried by the generic-retry interceptor). The shared deadline still covers the auth-retry silent-refresh + generic-retry backoff; 10 s is accepted with the understanding that a rare re-auth-tail false timeout may occur, in exchange for crisp UX.
- **Out of scope (recorded for a separate backend/infra track)**: backend `ConcertService` handler timeout (120 s) equal to the Gemini downstream timeout (120 s), and admin/organizer console APIs lacking a `GCPBackendPolicy` (inheriting the 30 s ALB default equal to their handler timeout). These are backend / `cloud-provisioning` concerns, not part of this change.
