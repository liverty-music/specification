## Context

See proposal.md (Why) for the observed breaks. The parts that shape the approach:

- Messaging is Watermill over NATS JetStream. Every publisher is `wotel.NewPublisherDecorator(pub)` (`internal/infrastructure/messaging/publisher.go:36,59`), and the router adds `wotel.Trace()` as its last middleware (`router.go:51`), after the poison queue, retry and recoverer middlewares. `wotel` is `github.com/voi-oss/watermill-opentelemetry` v0.1.3.
- `PublisherDecorator.Publish` starts a producer span from `messages[0].Context()` and stores the new context back on the message, then calls the inner publisher. `TraceHandler` starts a consumer span from `msg.Context()`. Neither touches `msg.Metadata`, so nothing crosses the broker.
- Message metadata does cross the broker: the `ce_*` CloudEvents attributes set in `messaging/cloudevents.go:44-48` arrive at the consumer (`adapter/event/analytics_consumer.go:579` reads `ce_time`).
- `pkg/telemetry/telemetry.go:38` installs `propagation.TraceContext{}` as the global propagator. The logger (`github.com/pannpers/go-logging` v1.3.0) adds `trace_id` and `span_id` from the span in the context to every line, so a correct context is enough to fix the logs.
- Jobs: `cmd/job/<name>/main.go` builds its app through `internal/di/*_job.go`, which calls `telemetry.SetupTelemetry`; the run loop (`concert-discovery/main.go:74`, `sales-phase-discovery/main.go:74`) passes the root `ctx` to the use case with no span.

## Goals / Non-Goals

**Goals:**

- The spec in `specs/components/infrastructure/backend/process/trace-propagation` holds for every publisher, every consumer and every job.
- The consumer span is a child of the producer span, not only of the caller, so a trace shows the publish step.

**Non-Goals:**

- Sampling changes. `TELEMETRY_SAMPLER_RATIO` stays as configured; an unsampled span still has a valid trace id, so logs keep the link either way.
- Trace links between an Order and the webhook that confirms it (the provider starts its own request), and frontend-to-backend propagation (already done by `otelconnect` and the fan app's fetch instrumentation).
- Replacing Watermill or the logger.

## Decisions

### Inject in a publisher decorator under `wotel`, not in `NewEventWithID`

Wrap the broker publisher in a small `traceContextPublisher` that, for each message, runs `otel.GetTextMapPropagator().Inject(msg.Context(), metadataCarrier(msg.Metadata))`, and put it inside the `wotel` decorator: `wotel.NewPublisherDecorator(traceContextPublisher{pub})`. `wotel` sets the producer span on the message context before it calls the inner publisher, so the injected `traceparent` names the producer span as parent.

- Alternative: inject in `NewEventWithID` (`cloudevents.go:35`). Rejected: it runs before `wotel` starts the producer span, so the consumer would hang off the caller and the publish step would be an orphan sibling.
- Alternative: fork or replace `wotel`. Rejected: it adds a dependency to own for two calls; the decorator and the middleware below are about 30 lines with tests.
- `metadataCarrier` adapts `message.Metadata` (a `map[string]string`) to `propagation.TextMapCarrier`; `propagation.MapCarrier(msg.Metadata)` works directly because the types match. Keys are the W3C names `traceparent` and `tracestate`, next to the `ce_*` keys.

### Extract in a router middleware placed just before `wotel.Trace()`

`extractTraceContext` sets `msg.SetContext(otel.GetTextMapPropagator().Extract(msg.Context(), carrier))`, and is added right before `wotel.Trace()` so the consumer span starts from the remote context. Placed after poison queue, retry and recoverer, so each retry attempt is a child span in the same trace, and a broker redelivery extracts the same context again. A message without `traceparent` leaves the context unchanged, and `wotel` starts a new root as today.

### One root span per artist in the search jobs, linked to the run span

Add `telemetry.StartJobRun(ctx, jobName)` and `telemetry.StartJobItem(runCtx, spanName, attrs...)` in `pkg/telemetry`. `StartJobItem` uses `trace.WithNewRoot()` and `trace.WithLinks(trace.LinkFromContext(runCtx))`. `concert-discovery` and `sales-phase-discovery` call `StartJobItem` per artist (`concert_search.artist`, `ticket_sale_search.artist`, with `artist.id`); the other jobs call only `StartJobRun`.

- Alternative: one trace per run. Rejected: a run touches hundreds of artists, so one trace would hold thousands of spans and the analytics layer could not key one search by its trace id.
- Alternative: new root per artist with no link. Rejected: the link keeps "which run did this" answerable from the trace.

### Correct the router comment

`router.go:50` states what the middlewares now do, and names the extract step.

## Risks / Trade-offs

- [More spans reach Cloud Trace: one per artist search plus the now-connected consumer spans] → most of these spans exist today as separate roots, so the count grows by the job spans only; Cloud Trace ingestion volume is checked in the billing export after the rollout (task 3.3).
- [A publisher and a consumer on different releases during a rollout] → an old consumer ignores the new metadata keys and an old publisher sends none; both cases fall back to today's behavior, so there is no ordering constraint.
- [`traceparent` in metadata is trusted from any publisher] → only backend processes publish to the broker; the context carries ids, not authority.

## Migration Plan

Ship in one backend release. Rollback is a revert: no data or wire format depends on the new keys.
