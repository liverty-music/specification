## Context

See proposal.md - Why. The facts that shape the approach:

- **Sampler**: `pkg/telemetry/telemetry.go:62` sets `sdktrace.ParentBased(sdktrace.TraceIDRatioBased(SamplerRatio))`, with `TELEMETRY_SAMPLER_RATIO` at its default 1.0, so every root span is recorded.
- **Where the parentless spans come from** (Trace API, 2026-10-28, every billable span of the day grouped by the kind of its trace's root):
  - 10,368 roots of kind client, each a lone `SELECT` from `internal/infrastructure/database/rdb` (`TracedPool`). The sweepers in `internal/di/*_sweeper_job.go`, `lottery_draw_job.go` and `organizer_reconciler.go` call their usecase with the process context, which holds no span.
  - 1,560 roots of kind client, `HTTP GET connectSettings` and `HTTP POST generateEphemeralCert` on `sqladmin.googleapis.com`, in the fan API, the event consumer and the workflow worker. `cloudsqlconn` v1.25.4 builds its Admin API client through `cloud.google.com/go/auth/httptransport`, which wraps the transport in `otelhttp` unless telemetry is disabled (`google.golang.org/api` v0.307.0 `transport/http/dial.go:309-312`). The refresh runs about once an hour and repeats 5 times, 30 seconds apart, in each process (observed; the repeat matches the connector's refresh-now rule for a certificate that expires within 4 minutes, `internal/cloudsql/instance.go:392-403`).
  - Every other root is a server span (Connect RPC), a job span (`pkg/telemetry/job.go`), a producer span or a workflow span. None of them is of kind client.
- **Logs**: `go-logging` adds `trace_id` and `span_id` from the span context in `ctx`. The OpenTelemetry Go SDK assigns the ids before it asks the sampler, so a span the sampler drops still has a valid trace id.

## Goals / Non-Goals

**Goals:**

- No root span of kind client is exported, from any process, whatever starts it.

**Non-Goals:**

- The spans Cloud SQL Query Insights writes (23,791 on 2026-10-28, more than the backend's own). They are not billed, they show slow query plans, and they are configured on the instance, not in the backend.
- `artist-image-sync` (one trace of about 1,100 spans a day). It is the work of a job run, which the spec keeps.
- Tracing the work a sweeper finds. The sweepers are being replaced by workflows (`make-lottery-draw-durable`, `unify-order-issuance`, `resell-tickets-by-lottery`), which record their runs. Until then a sweep that does something is followed in the logs, as today.
- Changing the sampling ratio.

## Decisions

### Drop client roots in the sampler

`setupTracerProvider` wraps the root sampler: `sdktrace.ParentBased(clientRootDrop{sdktrace.TraceIDRatioBased(ratio)})`. `clientRootDrop.ShouldSample` returns `Drop` when `p.Kind == trace.SpanKindClient`, and otherwise asks the wrapped sampler. `ParentBased` calls the root sampler only for a span without a parent, so a client span inside a request, an event, a job run or a workflow run follows its parent as today.

- A client span is an outgoing call: a database query, an HTTP call to Stripe or an Admin API. Without a parent it answers no question about any unit of work, and the spec says so.
- A producer span stays: an event published outside a unit of work (by a sweeper) starts the trace its consumer continues, and that work is worth reading.
- Rejected - an unsampled context in each sweeper's tick, plus `WithHTTPClient` on the Cloud SQL dialer with telemetry disabled: two mechanisms in six places, and the next sweeper or library that calls out without a span adds noise again.
- Rejected - drop the spans in a `SpanProcessor` before export: the span is still built and recorded first, and the sampler is the place the SDK provides for this choice.
- Rejected - filter in the OTLP collector: the rule would live in another repository's configuration, away from the tests that check it.

## Risks / Trade-offs

- [A unit of work that forgets to start its span loses its queries silently, where today they show up as parentless traces] → the spec requires a span for every request, event, job run and workflow run, and their tests check it; the log lines keep a trace id either way.
- [Stripe and Admin API calls made by a sweeper are no longer in Cloud Trace] → their errors are logged, and the sweepers move to workflows in the changes named above.

## Migration Plan

Ship in one backend release. Rollback is a revert; nothing stored depends on the sampler.

After the rollout, read-only in prod: list one hour of traces with the Trace API and confirm that no trace's root is of kind client, and that RPC and job traces still arrive. The next day, read the billing export's "Spans ingested" for the day and record it in this design.

### Result

Billing export, "Spans ingested", per billing day (America/Los_Angeles). The 14,984 above was counted before the export for 2026-10-28 was complete; the complete figure for that day is 15,577.

| Day | Spans ingested | Note |
|---|---|---|
| 2026-10-28 | 15,577 | before the rollout |
| 2026-10-29 | 7,023 | first full day after the rollout (v1.108.0, rolled out 2026-10-29 05:42 UTC) |

Hourly, the backend went from about 510 spans an hour before the rollout to about 107 an hour in the 16 hours after it. 3,743 of the day's spans fall in the single hour starting 2026-10-30 05:00 UTC, which no scheduled job explains. After the rollout, the Trace API showed no trace whose root span is of kind client (2026-10-29 05:43-06:43 and 09:00-09:40 UTC). RPC, job and consumer traces still arrived.
