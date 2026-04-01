## Why

The API server has a robust graceful shutdown via the `shutdown` package with phased teardown, but the event consumer and CronJob entry points have gaps that can cause message loss, resource leaks, and panics during termination. These issues are latent — they only manifest under SIGTERM timing pressure on Kubernetes — making them hard to detect in normal operation but critical for production reliability.

## What Changes

- **Fix Router/shutdown race in consumer**: The Watermill Router is not registered in any shutdown phase. On SIGTERM, `Router.Run(ctx)` begins closing asynchronously while `shutdown.Shutdown()` proceeds to close the publisher and database in parallel. This creates a race where in-flight handlers may fail DB writes or lose acks (especially with `AckAsync: true`). The Router will be integrated into the Drain phase so it fully stops before downstream resources are closed.
- **Fix HealthServer leak on DI failure**: The consumer starts a HealthServer goroutine before DI initialization. If DI fails, the HealthServer is never registered in shutdown and its goroutine leaks. A deferred close will be added immediately after starting the server.
- **Fix nil-pointer panic on DI failure in all entry points**: When DI fails, `run()` returns an error but the deferred `shutdown.Shutdown()` accesses `app.ShutdownTimeout` — a nil dereference. All four entry points (api, consumer, concert-discovery, artist-image-sync) will be guarded against this.

## Capabilities

### New Capabilities

(none — this is an infrastructure reliability fix)

### Modified Capabilities

(none — no spec-level behavior changes, only shutdown implementation)

## Impact

- **Backend entry points**: `cmd/api/main.go`, `cmd/consumer/main.go`, `cmd/job/concert-discovery/main.go`, `cmd/job/artist-image-sync/main.go`
- **DI wiring**: `internal/di/consumer.go` (Router registration in Drain phase)
- **Risk**: Low — changes are isolated to startup/shutdown paths and do not affect request handling or business logic
- **Testing**: Existing unit tests + manual SIGTERM verification on local Docker
