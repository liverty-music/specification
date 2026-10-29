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

### `normalize-venue-names` is out of scope

`cmd/job/normalize-venue-names` is a one-time migration, not a scheduled job: no Dockerfile target, `docker-bake.hcl` entry, k8s manifest or cloud-provisioning resource runs it, and it never calls `telemetry.SetupTelemetry`, so a run span there would go to the no-op tracer. It gets no span, and backend#680 deleted it after confirming that every prod `listed_venue_name` (2,728 rows) is already normalized.

### Correct the router comment

`router.go:50` states what the middlewares now do, and names the extract step.

## Risks / Trade-offs

- [More spans reach Cloud Trace: one per artist search plus the now-connected consumer spans] → most of these spans exist today as separate roots, so the count grows by the job spans only; Cloud Trace ingestion volume is checked in the billing export after the rollout (task 3.3).
- [A publisher and a consumer on different releases during a rollout] → an old consumer ignores the new metadata keys and an old publisher sends none; both cases fall back to today's behavior, so there is no ordering constraint.
- [`traceparent` in metadata is trusted from any publisher] → only backend processes publish to the broker; the context carries ids, not authority.

## Migration Plan

Ship in one backend release. Rollback is a revert: no data or wire format depends on the new keys.

## Production check (v1.95.0, 2026-10-23)

- 3.1: a manual run (`concert-discovery-manual-trace-1608`) logged a `trace_id` on all 7 `successfully received Gemini response` lines. For Clutch, the job lines and the `event-consumer` lines (`processing concert.discovered event`, venue search) share trace `f526dfd73adb2a8cc8fb28d37c8b4e14`. The `auto-published new concerts for series` line did not occur because both concerts were kept as reconciliation candidates; the owner accepted the `ingest-concert` lines as the evidence.
- 3.2: in Cloud Trace, trace `f526dfd73adb2a8cc8fb28d37c8b4e14` holds `concert_search.artist` (root) → the send span → `ingest-concert` and the consumer's SQL and HTTP spans (31 spans, every parent present), and `concert_search.artist` links to the run trace `686d53c3743e44a6289da87c9b68caf1` (owner checked the Links panel). v1.95.0 named the send span `messaging.traceContextPublisher`; backend#681 (v1.95.1) restored `nats.Publisher` by injecting through watermill's `MessageTransformPublisherDecorator` and naming the span explicitly, confirmed on a `USER.logged_in` trace (`712c5a0cc7aff1de47647c5813fb8eed`).
- 3.3 (billing export, read 2026-10-29): Cloud Trace bills one SKU, "Spans ingested". The 7 days before the rollout (2026-10-16 to 10-22 JST) ingested 137,847 spans (19,692 a day); the 6 full days after it (10-23 to 10-28) ingested 110,561 (18,427 a day). Both cost $0 inside the free tier. The rollout added no measurable volume; the 6% drop is not attributed to it. Read on day 6 instead of day 7 at the owner's request. The spans Cloud SQL Query Insights writes (query plans) are not billed: on 10-28 the Trace API returned 38,775 spans, of which 23,791 were query plans, and the remaining 14,984 equal that day's billed count. 11,928 of those 14,984 were client spans with no parent (sweeper queries and Cloud SQL Admin API certificate refreshes); `trace-only-units-of-work` stops recording them.
