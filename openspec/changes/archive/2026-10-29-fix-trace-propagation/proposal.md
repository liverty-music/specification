## Why

A trace in the backend stops at every NATS hop, and the scheduled jobs produce no trace at all. A Gemini call, the concert it discovers and the insert done by the `ingest-concert` consumer therefore carry unrelated `trace_id`s (or none), so neither Cloud Trace nor the logs can show one discovery end to end. The analytics work that follows (one PostHog `$ai_generation` and its outcome events per search, keyed by the trace) needs this link, and it was always meant to exist: `messaging/router.go:50` says the router propagates trace context through message metadata, but nothing does.

Observed in prod on 2026-10-20:

- `concert-discovery` job: the `successfully received Gemini response` lines have no `trace_id`.
- `search-first-followed-artist` consumer path: the Gemini call and the parse share one `trace_id`, but the `auto-published new concerts for series` line written by `ingest-concert` carries a different one.

Cause, read from the code:

- `github.com/voi-oss/watermill-opentelemetry` v0.1.3 starts the producer span and the consumer span from `msg.Context()` only (`publishers.go:47-78`, `subscribers.go:33-35`). It never writes `traceparent` into the message metadata and never reads it back, so the in-process context is lost when the message crosses NATS.
- The jobs set up telemetry (`internal/di/job.go:58`) but never start a span, so the context the use cases receive holds no trace.
- The W3C propagator is already installed (`pkg/telemetry/telemetry.go:38`); it is just never used for messages.

## What Changes

- Publishing an event writes the caller's trace context (`traceparent`, `tracestate`) into the message metadata, next to the CloudEvents `ce_*` attributes.
- Every event consumer reads that context back before its handler span starts, so the handler span is a child of the publisher's span and keeps its `trace_id`.
- `concert-discovery` and `sales-phase-discovery` start one root span per artist, linked to one span for the job run, so each artist search is its own trace instead of one trace holding hundreds of artists.
- The other jobs start one span per run, so events they publish (for example `SALES_PHASE.reminder_due` from `sales-reminders`) carry a trace.
- The misleading comment in `messaging/router.go` is corrected.

No wire format changes: the event payloads and the `ce_*` attributes stay as they are, and a message without `traceparent` (one published before the rollout) is handled as today, in a new trace.

## Capabilities

### New Capabilities

- `components/infrastructure/backend/process/trace-propagation`: one unit of work keeps one trace across every backend process it passes through, including event consumers fed through NATS and scheduled jobs.

### Modified Capabilities

None.

## Impact

- backend: `internal/infrastructure/messaging/publisher.go` (inject), `internal/infrastructure/messaging/router.go` (extract middleware, comment), `pkg/telemetry` (job span helpers), `cmd/job/concert-discovery/main.go`, `cmd/job/sales-phase-discovery/main.go` and the other `cmd/job/*` entry points (spans), with unit tests in `internal/infrastructure/messaging` and `pkg/telemetry`.
- No proto, frontend or cloud-provisioning change. No new dependency.
- Cloud Trace receives more connected spans; the volume per run does not change much, because each job span and consumer span exists already or replaces an untraced run.
