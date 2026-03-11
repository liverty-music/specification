## Why

Watermill logs are output as plain text via `watermill.NewStdLogger()`. On GKE with GCP Cloud Logging, these appear as `textPayload` and are misclassified as `severity: ERROR` (612 out of 1,324 logs). Switching to structured JSON output allows GCP to parse `jsonPayload` and correctly interpret log severity.

## What Changes

- Replace `watermill.NewStdLogger(false, false)` with `watermill.NewSlogLogger(logger.Slog())` in all 3 DI initialization functions (`consumer.go`, `provider.go`, `job.go`)
- Update `go-logging` dependency from v1.1.x to v1.2.0 which adds the `Slog()` method exposing the underlying `*slog.Logger`
- Thread the application `*logging.Logger` into watermill logger construction so both share the same slog handler (format, level, output)

## Capabilities

### New Capabilities

None.

### Modified Capabilities

None. This is a logging infrastructure change with no spec-level behavior impact.

## Impact

- **Backend DI layer**: `consumer.go`, `provider.go`, `job.go` — watermill logger construction changes
- **Dependency**: `github.com/pannpers/go-logging` v1.1.x → v1.2.0 (new `Slog()` method, [issue #3](https://github.com/pannpers/go-logging/issues/3))
- **GCP Cloud Logging**: Watermill logs will appear as `jsonPayload` with correct severity mapping
- **No breaking changes**: The watermill `LoggerAdapter` interface is unchanged; only the concrete implementation switches from `StdLogger` to `SlogLogger`
