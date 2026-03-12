## Context

The backend uses Watermill for async messaging (NATS JetStream in production, GoChannel locally). The `watermill-opentelemetry` library (`wotel`) is already a dependency and provides both a `Trace()` subscriber middleware and a `PublisherDecorator`.

Current state:
- **Publisher**: `NewEvent(data)` creates a `message.Message` with CloudEvents metadata but no `context.Context`. The message's internal context defaults to `context.Background()`. The publisher is **not** wrapped with `wotel.NewPublisherDecorator()`, so no trace context is injected into message metadata.
- **Consumer**: `wotel.Trace()` middleware is registered on the router and starts a span using `msg.Context()`. However, all 4 consumer handlers immediately discard it with `ctx := context.Background()`, losing trace information.
- **Logging**: `go-logging` v1.2.0 extracts `trace_id` and `span_id` from `context.Context` via `trace.SpanFromContext(ctx)`. When `context.Background()` is passed, `SpanContext.IsValid()` returns false and no trace fields are emitted.

## Goals / Non-Goals

**Goals:**
- Consumer structured logs include `trace_id` and `span_id` fields
- Publisher and Consumer share the same trace, enabling end-to-end distributed tracing across the message broker
- No new dependencies required

**Non-Goals:**
- Implementing baggage propagation (W3C Baggage)
- Adding trace context to CloudEvents `ce_` metadata attributes (traceparent is propagated via Watermill metadata, separate from CloudEvents attributes)
- Changing the global `TextMapPropagator` — `wotel` uses its own internal propagation via message metadata keys

## Decisions

### 1. Use `msg.Context()` in consumer handlers instead of `context.Background()`

The `wotel.Trace()` middleware already calls `msg.SetContext(ctx)` with a span-enriched context before invoking the handler. Handlers just need to read it.

**Alternative considered**: Extract trace context manually from message metadata using `propagation.TraceContext{}`. Rejected because the middleware already does this — manual extraction would duplicate work.

### 2. Add `context.Context` parameter to `NewEvent()`

Change signature from `NewEvent(data any)` to `NewEvent(ctx context.Context, data any)` and call `msg.SetContext(ctx)`. This passes the caller's trace context into the message so that the publisher decorator can extract it.

**Alternative considered**: Set context at the `publishEvent()` call site instead of in `NewEvent()`. Rejected because `NewEvent` is the message factory — context attachment belongs with message creation for consistency.

### 3. Wrap Publisher with `wotel.NewPublisherDecorator()`

The decorator intercepts `Publish()`, extracts trace context from `msg.Context()`, and injects it into message metadata as Watermill metadata keys. The consumer-side `wotel.Trace()` middleware reads these keys back and restores the trace context.

This is necessary because message context does not survive serialization over NATS — only metadata does.

**Alternative considered**: Manually inject/extract traceparent into CloudEvents `ce_traceparent` attribute. Rejected because `wotel` already has a well-tested metadata-based propagation mechanism, and mixing propagation strategies adds complexity.

## Risks / Trade-offs

- **[Risk] Breaking change to `NewEvent()` signature** → All call sites must be updated to pass `ctx`. This is a compile-time breakage, so the compiler catches any missed call sites. Mitigation: update all call sites in the same PR.
- **[Risk] Publisher decorator adds per-message span overhead** → Each published message gets a producer span. This is expected behavior for distributed tracing and the overhead is negligible. The `AlwaysSample` tracer is already in use.
- **[Trade-off] GoChannel vs NATS behavior difference** → With GoChannel (local dev), `msg.Context()` is preserved in-process without metadata serialization, so tracing works even without the decorator. With NATS, the decorator is required. The decorator works correctly in both cases, so we apply it unconditionally.
