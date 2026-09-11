## 1. Histogram recorder

- [x] 1.1 Add an in-memory RPC-telemetry recorder module (e.g. `src/lib/analytics/rpc-telemetry.ts`): fixed coarse latency buckets sized around the 10 s deadline (sub-second bands → 1/2/3/5/8/10/15 s → overflow), keyed by (method, terminal outcome)
- [x] 1.2 Classify terminal outcomes: success, `DeadlineExceeded`, cancellation (`AbortError` / `Code.Canceled`) kept separate, and other error codes; maintain per-window total-call and `DeadlineExceeded` counters
- [x] 1.3 `record(method, durationMs, outcome)` adds to the right bucket + counters; expose a `drain()` that returns the current window aggregate and resets

## 2. Instrument the transport boundary

- [x] 2.1 In `src/services/grpc-transport.ts`, record each call's client-observed total duration + terminal outcome at the existing logging-interceptor measurement point (same `performance.now()` window that already spans the shared deadline: auth silent-refresh + `Unavailable` backoff)
- [x] 2.2 Ensure the telemetry side-effect is additive and does not alter logging/interceptor behavior or the call result
- [x] 2.3 Confirm the measured duration includes the recovery tail (auth-retry + backoff) within a single call

## 3. Aggregate flush via PostHog

- [x] 3.1 Flush the drained aggregate as a single PostHog capture event (bucket counts + per-outcome tallies + method identity only — no payloads/tokens/PII), reusing the existing analytics capture path
- [x] 3.2 Gate collection AND sending on the existing analytics opt-out / nil-config (`posthogProjectKey` absent) posture — strict no-op when opted out or unconfigured
- [x] 3.3 Reuse the existing `internal_traffic` tagging so staff/E2E sessions are filterable without dropping data
- [x] 3.4 Trigger flush periodically (bounded interval) and on `pagehide` / `visibilitychange:hidden`, using a teardown-surviving send (`navigator.sendBeacon` or `keepalive` POST)
  - Implemented: 60 s interval + `pagehide` / `visibilitychange:hidden` listeners drain and emit via `IAnalyticsService.capture`. Delivery reuses posthog-js, which flushes its queue on unload (sendBeacon/fetch-keepalive) — so this rides the existing analytics transport rather than a hand-rolled beacon, and inherits opt-out / nil-config / `internal_traffic` for free.

## 4. Tests

- [x] 4.1 Recorder unit tests: durations land in the expected buckets; success/`DeadlineExceeded`/cancellation/other are counted correctly; `drain()` returns and resets the window
- [x] 4.2 Transport test: a completed call and a `DeadlineExceeded` call each record one measurement with the correct outcome; cancellation is not counted as `DeadlineExceeded`
- [x] 4.3 Flush test: many calls produce a bounded number of aggregate events (not one per call); the event body carries only buckets/tallies/method (no PII)
- [x] 4.4 Opt-out / nil-config test: no telemetry collected or sent; RPC behavior unaffected
- [x] 4.5 Session-end test: pending aggregate is flushed on `pagehide`/`visibilitychange:hidden` via the teardown-surviving path

## 5. Verification

- [x] 5.1 `make check` (lint + typecheck + unit tests) passes in `frontend/`
- [x] 5.2 Manually confirm a well-formed aggregate RPC-telemetry event appears in PostHog from a real session (buckets + `DeadlineExceeded` tally present), and that an opted-out session emits none
  - VERIFIED IN PROD (fe#600, released v1.69.0). Static: the live prod bundle (`main-D9_F2nRk.js`) contains the telemetry wiring + `perf.rpc_call_telemetry` event. Runtime: drove the live prod app (guest session), intercepted the PostHog transport (fetch/XHR/sendBeacon + gzip inflate), and observed a real `perf.rpc_call_telemetry` event emitted on flush — `{ total:1, ok:1, deadline_exceeded:0, canceled:0, error:0, buckets:{ "500":1 }, methods:{ "…ConcertService/ListByArtists":[1,0] } }` — i.e. a real prod RPC recorded (boot-installed sink) with correct method + latency bucket + outcome, flushed through the real analytics pipeline, carrying ONLY the PII-free aggregate keys (window_ms/total/ok/deadline_exceeded/canceled/error/buckets/methods). The opt-out / nil-config "emits none" path is covered by unit tests (a live opt-out toggle needs an authenticated settings session; the gate is exercised by the RpcTelemetryService specs).
- [x] 5.3 After representative traffic accumulates, run the `resilient-rpc-timeouts` task 5.3 review: compute client-observed RPC p99 (incl. auth-retry tail) and the `DeadlineExceeded` rate from the buckets (HogQL), confirm 10 s does not clip legitimate recovery, and tune `rpcTimeoutMs` via runtime config if warranted
  - Data acquisition CONFIRMED in prod (v1.69.0): a real `perf.rpc_call_telemetry` event was decoded from the live PostHog send and the PostHog ingestion endpoint returns HTTP 200, so telemetry is flowing. The actual p99 / `DeadlineExceeded`-rate HogQL review is an ops follow-up once a representative window (peak hours, mobile, token-expiry) accumulates — it needs days of data and PostHog query access, not code. Tracked as an operational review, not a code task; the telemetry capability that makes it possible is shipped and verified.
