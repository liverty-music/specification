## 1. Publisher-side trace context injection

- [x] 1.1 Add `context.Context` parameter to `NewEvent()` in `internal/infrastructure/messaging/cloudevents.go` and call `msg.SetContext(ctx)`
- [x] 1.2 Update `NewEvent()` call site in `internal/usecase/concert_uc.go` to pass `ctx`
- [x] 1.3 Update `NewEvent()` call site in `internal/usecase/concert_creation_uc.go` to pass `ctx`
- [x] 1.4 Update `NewEvent()` call site in `internal/usecase/artist_uc.go` to pass `ctx`

## 2. Publisher decorator for metadata propagation

- [x] 2.1 Wrap the publisher with `wotel.NewPublisherDecorator()` in `internal/infrastructure/messaging/publisher.go`

## 3. Consumer-side trace context usage

- [x] 3.1 Replace `ctx := context.Background()` with `ctx := msg.Context()` in `internal/adapter/event/concert_consumer.go`
- [x] 3.2 Replace `ctx := context.Background()` with `ctx := msg.Context()` in `internal/adapter/event/artist_consumer.go`
- [x] 3.3 Replace `ctx := context.Background()` with `ctx := msg.Context()` in `internal/adapter/event/venue_consumer.go`
- [x] 3.4 Replace `ctx := context.Background()` with `ctx := msg.Context()` in `internal/adapter/event/notification_consumer.go`

## 4. Verification

- [x] 4.1 Run `make check` to verify compilation and tests pass
- [x] 4.2 Verify consumer logs include `trace_id` and `span_id` fields (local test with GoChannel)
