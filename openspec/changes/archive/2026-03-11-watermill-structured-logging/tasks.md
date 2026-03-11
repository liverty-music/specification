## 1. Dependency Update

- [x] 1.1 Run `go get github.com/pannpers/go-logging@v1.2.0` in backend/ to update go-logging dependency

## 2. DI Layer Changes

- [x] 2.1 Update `internal/di/provider.go`: replace `watermill.NewStdLogger(false, false)` with `watermill.NewSlogLogger(logger.Slog())` in `InitializeApp()`
- [x] 2.2 Update `internal/di/consumer.go`: replace `watermill.NewStdLogger(false, false)` with `watermill.NewSlogLogger(logger.Slog())` in `InitializeConsumerApp()`
- [x] 2.3 Update `internal/di/job.go`: replace `watermill.NewStdLogger(false, false)` with `watermill.NewSlogLogger(logger.Slog())` in `InitializeJobApp()`

## 3. Verification

- [x] 3.1 Run `make check` to ensure linting and tests pass
- [x] 3.2 Verify locally that watermill logs output as JSON (run with `LOG_FORMAT=json`)
