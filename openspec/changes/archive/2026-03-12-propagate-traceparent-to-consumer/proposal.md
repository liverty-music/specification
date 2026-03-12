## Why

Consumer process structured logs are missing `trace_id` and `span_id` fields, breaking distributed tracing continuity between Publisher and Consumer. This makes it impossible to trace event-driven processing end-to-end in Cloud Trace.

## What Changes

- Fix consumer handlers to use `msg.Context()` instead of `context.Background()`, propagating the trace context injected by the Watermill OTel middleware into logs and downstream processing
- Pass `context.Context` to `NewEvent()` and call `msg.SetContext(ctx)` so the caller's trace context is attached to the message
- Wrap the Publisher with `wotel.NewPublisherDecorator()` to inject traceparent into NATS message metadata, ensuring trace continuity across the message broker

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

(none — this is an implementation-level fix, no spec-level behavior changes)

## Impact

- **backend**: `internal/infrastructure/messaging/` — `cloudevents.go`, `publisher.go`, `router.go` (add Publisher decorator)
- **backend**: `internal/adapter/event/` — all consumer handlers (`concert_consumer.go`, `notification_consumer.go`, `venue_consumer.go`, `artist_consumer.go`)
- **backend**: `internal/usecase/` — all `NewEvent()` call sites (add `ctx` argument)
- **dependency**: `github.com/voi-oss/watermill-opentelemetry` (already present, no new dependency needed)
