## 1. Histogram recorder

- [ ] 1.1 Add an in-memory RPC-telemetry recorder module (e.g. `src/lib/analytics/rpc-telemetry.ts`): fixed coarse latency buckets sized around the 10 s deadline (sub-second bands → 1/2/3/5/8/10/15 s → overflow), keyed by (method, terminal outcome)
- [ ] 1.2 Classify terminal outcomes: success, `DeadlineExceeded`, cancellation (`AbortError` / `Code.Canceled`) kept separate, and other error codes; maintain per-window total-call and `DeadlineExceeded` counters
- [ ] 1.3 `record(method, durationMs, outcome)` adds to the right bucket + counters; expose a `drain()` that returns the current window aggregate and resets

## 2. Instrument the transport boundary

- [ ] 2.1 In `src/services/grpc-transport.ts`, record each call's client-observed total duration + terminal outcome at the existing logging-interceptor measurement point (same `performance.now()` window that already spans the shared deadline: auth silent-refresh + `Unavailable` backoff)
- [ ] 2.2 Ensure the telemetry side-effect is additive and does not alter logging/interceptor behavior or the call result
- [ ] 2.3 Confirm the measured duration includes the recovery tail (auth-retry + backoff) within a single call

## 3. Aggregate flush via PostHog

- [ ] 3.1 Flush the drained aggregate as a single PostHog capture event (bucket counts + per-outcome tallies + method identity only — no payloads/tokens/PII), reusing the existing analytics capture path
- [ ] 3.2 Gate collection AND sending on the existing analytics opt-out / nil-config (`posthogProjectKey` absent) posture — strict no-op when opted out or unconfigured
- [ ] 3.3 Reuse the existing `internal_traffic` tagging so staff/E2E sessions are filterable without dropping data
- [ ] 3.4 Trigger flush periodically (bounded interval) and on `pagehide` / `visibilitychange:hidden`, using a teardown-surviving send (`navigator.sendBeacon` or `keepalive` POST)

## 4. Tests

- [ ] 4.1 Recorder unit tests: durations land in the expected buckets; success/`DeadlineExceeded`/cancellation/other are counted correctly; `drain()` returns and resets the window
- [ ] 4.2 Transport test: a completed call and a `DeadlineExceeded` call each record one measurement with the correct outcome; cancellation is not counted as `DeadlineExceeded`
- [ ] 4.3 Flush test: many calls produce a bounded number of aggregate events (not one per call); the event body carries only buckets/tallies/method (no PII)
- [ ] 4.4 Opt-out / nil-config test: no telemetry collected or sent; RPC behavior unaffected
- [ ] 4.5 Session-end test: pending aggregate is flushed on `pagehide`/`visibilitychange:hidden` via the teardown-surviving path

## 5. Verification

- [ ] 5.1 `make check` (lint + typecheck + unit tests) passes in `frontend/`
- [ ] 5.2 Manually confirm a well-formed aggregate RPC-telemetry event appears in PostHog from a real session (buckets + `DeadlineExceeded` tally present), and that an opted-out session emits none
- [ ] 5.3 After representative traffic accumulates, run the `resilient-rpc-timeouts` task 5.3 review: compute client-observed RPC p99 (incl. auth-retry tail) and the `DeadlineExceeded` rate from the buckets (HogQL), confirm 10 s does not clip legitimate recovery, and tune `rpcTimeoutMs` via runtime config if warranted
