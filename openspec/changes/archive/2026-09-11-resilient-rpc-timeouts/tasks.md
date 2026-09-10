## 1. Runtime config plumbing

- [x] 1.1 Add optional `rpcTimeoutMs` to the `AppConfig` type in `shared/config/app-config.ts`, validated as an optional positive number
- [x] 1.2 Default `rpcTimeoutMs` to `10_000` when absent/invalid during validation (define a named constant, e.g. `DEFAULT_RPC_TIMEOUT_MS`); ensure a malformed value falls back rather than failing bootstrap
- [x] 1.3 Add the optional `rpcTimeoutMs` field to the tracked `config.json` (default 10 s applies when absent)
- [x] 1.4 (Optional follow-up, not required) Add the per-environment `rpcTimeoutMs` override to `cloud-provisioning` ConfigMaps if per-env tuning is desired
  - DESCOPED — optional infra follow-up, never in this change's committed scope. No ConfigMap override was added; prod is verified serving the built-in 10 s fallback (prod `config.json` omits `rpcTimeoutMs`, resolver returns `DEFAULT_RPC_TIMEOUT_MS`). Can be added later without a rebuild if per-env tuning is ever needed.

## 2. Apply the default RPC timeout

- [x] 2.1 Pass `defaultTimeoutMs: config.rpcTimeoutMs` into `createConnectTransport(...)` in `src/services/grpc-transport.ts`
- [x] 2.2 Confirm no per-method/per-call `timeoutMs` overrides are added (single default only)
- [x] 2.3 Verify the value flows through all three apps (fan-web, admin, organizer) via the shared transport factory

## 3. Bound the Service-Worker fetches

- [x] 3.1 Add `AbortSignal.timeout(~10_000)` to the PostHog capture `fetch()` in `src/lib/analytics/notification-interaction.ts` (`sendInteraction`); confirm an abort takes the existing throw → stash → Background-Sync resend path with the reused `$insert_id`
- [x] 3.2 Add `AbortSignal.timeout(~5_000)` to the cache-miss `fetch()` in `src/lib/push/push-renewal.ts` (`readVapidPublicKeyCacheFirst`); confirm an abort returns `null` (skip renewal, retry later) without throwing

## 4. Tests

- [x] 4.1 Unit-test `AppConfig` validation: present value is used; absent/invalid falls back to 10s
- [x] 4.2 Test that the transport is constructed with `defaultTimeoutMs` from config (fake config → assert transport option)
- [x] 4.3 Test `sendInteraction` timeout path: a stalled fetch aborts and is stashed for resend (reused insert_id)
- [x] 4.4 Test `readVapidPublicKeyCacheFirst` timeout path: a stalled cache-miss fetch aborts and returns `null` without throwing
- [x] 4.5 (Optional) Test that an RPC exceeding the deadline rejects with `Code.DeadlineExceeded` and is not retried

## 5. Verification

- [x] 5.1 `make check` (lint + typecheck + unit tests) passes in `frontend/`
- [x] 5.2 Manually confirm a hung RPC aborts at ~10s (e.g. against a stalled/slow endpoint) and the app surfaces the error instead of an infinite spinner
  - Shipped to prod as v1.68.0 (fe#597). Verified in the live prod bundle: fan-web transport wires `createConnectTransport({ defaultTimeoutMs: config.rpcTimeoutMs, … })` and the config resolver falls back to `10000` because prod `config.json` omits `rpcTimeoutMs`; SW carries both `AbortSignal.timeout` bounds. Runtime-confirmed in the prod browser: `AbortSignal.timeout` (the primitive connect-web applies) fires at the configured delay with a `TimeoutError` reason (→ `Code.DeadlineExceeded`) and aborts an in-flight fetch, while a fast request with the generous deadline completes normally. A full authenticated hung-RPC-through-the-UI E2E was not driven (needs prod creds + a genuinely stalling method; the only slow backend RPC, `SearchNewConcerts`, is not called from the frontend and triggering it has Gemini cost/side-effects — deliberately avoided). The not-retried-on-`DeadlineExceeded` behavior is covered by unit test 4.5.
- [x] 5.3 Post-ship: review OTel RPC-duration p99 (including the auth-retry path) to confirm 10s does not clip legitimate recovery; adjust `rpcTimeoutMs` via config if needed
  - PARTIALLY VERIFIED + DEFERRED to a follow-up change. Measurable proxy is green: prod Cloud Trace over 24h (1000+ traces) shows 0 RPCs ≥ 5 s, exactly 1 request ≥ 3 s (a non-RPC `HTTP GET`), ~99.5% < 1 s — server-observed durations leave a wide margin under the 10 s deadline, so normal operations are not clipped. The core of 5.3 — the client-side total-call p99 *including the auth silent-refresh + retry-backoff tail* — is NOT measurable with current instrumentation: the frontend exports no OTel spans (`otel-init.ts` only propagates `traceparent`) and the Zitadel refresh round-trip is excluded from tracing. A separate change will add client-side telemetry (span export and/or a client-side `DeadlineExceeded` counter) to close this. The residual auth-retry-tail risk is already accepted by design D2 and mitigated by the runtime `rpcTimeoutMs` config knob (raise without a rebuild if telemetry later shows false timeouts).
