## Context

The backend uses `watermill.NewStdLogger(false, false)` in 3 DI files to create watermill's logger. This produces unstructured text output (`textPayload` in GCP). Meanwhile, the application logger (`*logging.Logger` from `go-logging`) already outputs structured JSON via slog when configured with `FormatJSON`.

Watermill v1.5.1 ships `watermill.NewSlogLogger(*slog.Logger)` which accepts a standard `*slog.Logger` and maps watermill log levels to slog levels. The `go-logging` v1.2.0 release adds `Slog()` to expose the underlying `*slog.Logger`.

## Goals / Non-Goals

**Goals:**
- Watermill logs output as structured JSON (`jsonPayload`) in GCP Cloud Logging
- GCP correctly classifies log severity based on the `severity` field in JSON
- Watermill and application logs share the same slog handler (consistent format, level, destination)

**Non-Goals:**
- Custom level mapping (watermill's default slog level mapping is sufficient)
- Changing watermill's log verbosity (keep debug/trace disabled as today)
- Modifying the `go-logging` library beyond what v1.2.0 already provides

## Decisions

### 1. Use `watermill.NewSlogLogger` over custom adapter

**Decision:** Use Watermill's official `watermill.NewSlogLogger()` rather than writing a custom `LoggerAdapter`.

**Alternatives considered:**
- Custom `LoggerAdapter` wrapping `*logging.Logger` — more control but unnecessary maintenance burden
- `watermill.NewSlogLoggerWithLevelMapping` — useful if we needed custom level mapping, but defaults are fine (Trace→Debug, Debug→Debug, Info→Info, Error→Error)

**Rationale:** Official adapter is maintained by the Watermill team, handles all edge cases, and directly accepts `*slog.Logger`.

### 2. Thread `*logging.Logger` into DI functions

**Decision:** Pass the existing application `*logging.Logger` into each DI init function and derive the watermill logger via `watermill.NewSlogLogger(logger.Slog())`.

**Rationale:** This ensures watermill uses the same slog handler (format, level, output) as the rest of the application. No separate logger configuration needed.

### 3. Replace in all 3 DI entry points

**Decision:** Update `consumer.go`, `provider.go`, and `job.go` simultaneously.

**Rationale:** All three use identical `watermill.NewStdLogger(false, false)` patterns. Partial migration would leave inconsistent logging behavior.

## Risks / Trade-offs

- **Log volume increase** → Watermill's slog adapter may include more structured fields per log line than StdLogger. Monitor log volume after deployment. Mitigation: slog level filtering already applies.
- **Behavioral difference in level mapping** → Watermill's Trace maps to slog Debug. Since trace is disabled (`NewStdLogger(false, false)`), this has no practical impact. `NewSlogLogger` respects the slog handler's level, so Debug logs will be filtered by the configured slog level.
