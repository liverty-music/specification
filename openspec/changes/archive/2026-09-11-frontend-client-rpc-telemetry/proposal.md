## Why

The shipped `resilient-rpc-timeouts` change (frontend v1.68.0) added a **10 s default client-side RPC deadline**, but its post-ship review task (5.3) — confirm the 10 s deadline does not clip legitimate recovery, *including the auth silent-refresh + retry-backoff tail* called out in that change's design D2 — is currently **unverifiable**. The frontend exports **no OpenTelemetry spans** (`otel-init.ts` only propagates `traceparent` to the backend) and the Zitadel silent-refresh round-trip is deliberately excluded from tracing, so the **client-observed** RPC duration (the exact quantity the deadline bounds) is invisible in production. Backend Cloud Trace only sees the server-side portion — it cannot capture the re-auth tail or the client-side retry backoff, and there is no signal at all for how often the deadline actually fires (`DeadlineExceeded` rate). Without this, the deadline value cannot be tuned from data.

## What Changes

- Introduce **client-side RPC telemetry** for the consumer (fan-web) shared transport: at the interceptor boundary that already measures per-call wall-clock, record every **client-observed** RPC's *total* duration — spanning the whole recovery sequence (auth silent-refresh + transient-`Unavailable` retry backoff), i.e. exactly what the single call deadline bounds — into an in-memory **bucketed histogram**, tagged by terminal outcome (success vs. `Code`, with `DeadlineExceeded` distinguished).
- Maintain a **`DeadlineExceeded` occurrence counter** (and total-call counter) so the deadline-firing *rate* is observable, not just the latency distribution.
- **Flush aggregated snapshots** (histogram bucket counts + per-outcome tallies for the window) through the **already-wired PostHog capture path**, periodically and on `pagehide` / `visibilitychange:hidden`, as a small number of events per session — **not** one event per RPC. Percentiles (p95/p99) are computed **at query time** from the bucket counts (HogQL), per RUM best practice (ship the distribution, not pre-computed percentiles).
- No per-RPC event, **no new infrastructure**, and **no CSP change** (the PostHog capture host is already allowed). Analytics opt-out and nil-config (`posthogProjectKey` absent) are honored — telemetry is a strict no-op in those states, mirroring the existing analytics posture.
- This makes `resilient-rpc-timeouts` task 5.3 **dischargeable**: once representative traffic accumulates, review the client-observed RPC p99 (including the auth-retry tail) and the `DeadlineExceeded` rate to confirm 10 s does not clip legitimate recovery, and tune `rpcTimeoutMs` via runtime config if the data warrants.

Scope note: the consumer (fan-web) transport is the target — it carries the real-user, mobile, token-expiry traffic where the re-auth tail matters. The admin/organizer consoles (low-volume internal tools) are an optional later extension and are out of scope here.

## Capabilities

### New Capabilities
(none — see design.md)

### Modified Capabilities
<!-- None. This is additive client-side observability. The `frontend-network-timeouts`
     capability's requirements (the deadline itself) are unchanged; this change only
     adds the telemetry needed to review/tune it, and does not alter any existing
     `product-analytics` scenario (it adds an aggregate event, changes no existing one). -->

## Impact

- **Repository**: `frontend/` only. No proto, backend, or cloud-provisioning changes; no BSR dependency.
- **Code**:
  - `src/services/grpc-transport.ts` — add a telemetry interceptor (or extend the existing logging interceptor's duration measurement) that records each client-observed RPC's total duration + terminal outcome into the histogram recorder.
  - A new small `src/lib/analytics/` (or `src/services/`) module — the in-memory bucketed-histogram recorder + aggregate-flush logic, reusing the existing PostHog capture path and the analytics opt-out / nil-config gate.
  - Wire flush triggers (periodic + `pagehide`/`visibilitychange`) in the app lifecycle.
  - Optional: an additive runtime-config field (e.g. flush interval / sampling) — only if tuning without a rebuild is wanted; defaults are fine otherwise.
- **Behavior**: Additive. A few aggregate analytics events per session; no change to RPC behavior, no per-request overhead beyond the existing duration measurement. Honors analytics opt-out and nil-config (no events sent).
- **Downstream**: Discharges `resilient-rpc-timeouts` task 5.3 (post-ship p99 / `DeadlineExceeded`-rate review and data-driven `rpcTimeoutMs` tuning).
