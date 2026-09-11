## Context

See proposal.md — Why. Constraints that shape the approach:

- The frontend already builds its shared consumer transport in `src/services/grpc-transport.ts`, whose `loggingInterceptor` **already measures** each call's wall-clock (`performance.now()` start → terminal) and knows the terminal `Code`. The single call deadline is shared across the interceptor chain (auth silent-refresh + `Unavailable` backoff), so a duration measured at this boundary already spans the full recovery tail — exactly what the deadline bounds.
- A **PostHog analytics path is already wired** (`src/lib/analytics/…`, `AnalyticsService`), including the nil-config gate (`posthogProjectKey` absent → no SDK init, everything dropped) and an opt-out flag. The PostHog capture host is already in CSP.
- The frontend exports **no OTel spans** by design (`otel-init.ts` propagates `traceparent` only); adding browser→collector export would require new always-on infrastructure (an OTLP receiver), CORS, CSP, sampling, and auth.
- Production RPC volume is modest (order of hundreds–low-thousands of calls/day observed in Cloud Trace), so *ingestion* cost is within every vendor free tier for all candidate designs — the real differentiator is implementation/operational weight.

## Goals / Non-Goals

**Goals:**
- Capture the **client-observed** RPC duration distribution (incl. the auth-retry tail) and the `DeadlineExceeded` rate, as bucketed aggregates, at the existing transport boundary.
- Report via the existing analytics channel with **no new infrastructure, no CSP change, and no per-RPC event**.
- Discharge `resilient-rpc-timeouts` task 5.3: enough data to review p99 (incl. re-auth tail) and tune `rpcTimeoutMs` from evidence.

**Non-Goals:**
- Distributed / per-request tracing or front-to-back trace correlation (deliberately not built; would be the Cloud-Trace-collector path).
- Real-time alerting on RPC latency (this is a periodic review signal; alerting can be layered later from the same data).
- Telemetry for the admin/organizer consoles (low-volume internal tools; optional later extension).
- Server-side metrics changes (no backend/proto work).

## Decisions

**D1 — Aggregate a client-side bucketed histogram; do not emit per-RPC events.**
Record each terminal call into an in-memory histogram keyed by (method, outcome) with fixed latency buckets, plus per-outcome counters. Flush aggregate snapshots (bucket counts + tallies) periodically and on page-hide. Percentiles are computed **at query time** (HogQL) from the buckets. Rationale: RUM best practice is to ship the distribution, not pre-computed percentiles (a per-session p99 cannot be recombined into a fleet p99); aggregation keeps event volume ~per-session instead of per-RPC, staying trivially within PostHog's free tier and avoiding a "4× event" cost trap. Alternative (one event per RPC) rejected: high volume, and still needs query-time aggregation anyway.

**D2 — Report through the already-wired PostHog capture path (chosen over Cloud Trace collector and a backend telemetry RPC).**
All three candidates cost ~$0 to ingest at this app's volume; they differ in implementation/ops weight (researched and compared with the user):
- **PostHog aggregate flush (chosen)** — frontend-only, reuses the existing capture + opt-out/nil-config gate, no new infra, no CSP change. Fastest path to a dischargeable 5.3.
- **Backend telemetry RPC → Cloud Monitoring distribution metric (runner-up)** — histogram-native and co-located with existing backend metrics/alerts, but needs a proto change + backend handler + BSR release cycle (cross-repo). Revisit if RPC telemetry should live in Cloud Monitoring rather than PostHog.
- **Browser → Cloud Trace via an OTLP collector (rejected)** — highest infra/ops cost (an always-on collector service + CORS/CSP/sampling/auth) and yields distributed tracing that 5.3 does not need.

**D3 — Instrument at the existing transport boundary, reusing the logging interceptor's measurement.**
Extend/adjoin the `loggingInterceptor` (or add a sibling telemetry interceptor in the same chain) so the recorded duration is the same wall-clock the logger already computes, guaranteeing the measurement spans the shared deadline window (auth-retry + backoff). No per-call-site changes. Cancellation (`AbortError` / `Code.Canceled`) is classified separately from `DeadlineExceeded` so user-navigation cancels don't pollute the deadline-firing rate.

**D4 — Delivery that survives teardown; opt-out/nil-config is a hard gate.**
On `pagehide` / `visibilitychange:hidden`, flush via a teardown-surviving send (e.g. `navigator.sendBeacon` or a `keepalive` POST) so the final window isn't lost. The recorder consults the same opt-out / nil-config gate as the rest of analytics **before** collecting or sending — when opted out or unconfigured it is a strict no-op (no collection, no events). Payload is method identity + bucket counts + outcome tallies only — no request/response content, tokens, or PII.

**D5 — Fixed, coarse latency buckets sized around the 10 s deadline.**
Use a small fixed bucket set with good resolution up to and across 10 s (e.g. sub-second bands, then 1/2/3/5/8/10/15 s, plus an overflow bucket) so both the sub-second common case and the near-/over-deadline tail are legible, and the over-10 s bucket directly shows deadline pressure. Buckets are a compile-time constant; a runtime-config knob is unnecessary for a review signal (can be added later if needed).

## Risks / Trade-offs

- **PostHog dependency for perf data** → RPC observability lives in the analytics tool, not a dedicated APM. Mitigation: acceptable for a periodic review signal; the aggregate shape (buckets + tallies) is portable, so a later move to Cloud Monitoring (runner-up D2) is a re-point, not a re-model.
- **Low volume → slow to reach significance** → at hundreds–thousands of calls/day, a meaningful p99 (esp. the rare re-auth tail) needs days of accumulation. Mitigation: 5.3 is an offline post-ship review, not real-time; wait for a representative window (peak hours, mobile, token-expiry events) before concluding.
- **Opt-out / internal-traffic skew** → opted-out and staff sessions are excluded/tagged, so the sample may under-represent some cohorts. Mitigation: reuse the existing `internal_traffic` tagging so staff/E2E can be filtered without dropping data; accept opt-out exclusion as the privacy cost.
- **Aggregation loses per-request detail** → a pathological single slow call isn't individually inspectable. Mitigation: that is the intended trade-off (D1); if a specific slow path needs drill-down, that is the Cloud-Trace path, out of scope here.
- **Double counting vs. the logging interceptor** → reusing the same measurement must not change logging behavior. Mitigation: the telemetry side-effect is additive and guarded; if a separate interceptor is used it observes the same terminal event without altering the chain.

## Migration Plan

Additive, frontend-only. Ship behind the existing analytics gate (no-op when analytics is unconfigured), release with the normal frontend flow, and verify a well-formed aggregate event appears in PostHog from a real session. Rollback = revert the frontend change; no data model or infra to unwind. Once representative data accumulates, perform the `resilient-rpc-timeouts` 5.3 review from this data.
