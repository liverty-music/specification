## Why

The Gemini concert search logs the same error at ERROR level in two layers (infrastructure and usecase), causing Cloud Monitoring to create duplicate alert incidents from a single failure. Additionally, `isRetryable` does not cover HTTP 401, so transient Workload Identity token refresh failures are treated as permanent errors instead of being retried.

## What Changes

- Demote the infrastructure-layer log (`gemini model call failed` in `searcher.go`) from ERROR to WARN so that only the usecase-layer log (`background concert search failed` in `concert_uc.go`) triggers alerts.
- Add HTTP 401 (Unauthorized) to `isRetryable` in `errors.go` so that transient WI credential failures are retried with exponential backoff.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `app-error-log-alerting`: No spec-level requirement changes. The alerting policy and its `severity="ERROR"` filter remain the same. The change is purely in which application code emits ERROR vs WARN logs.

## Impact

- **backend** (`internal/infrastructure/gcp/gemini/searcher.go`): Log level change from ERROR to WARN.
- **backend** (`internal/infrastructure/gcp/gemini/errors.go`): `isRetryable` function updated to include 401.
- **Alerting behavior**: Duplicate incidents from a single Gemini failure will no longer occur because only one ERROR log line (from the usecase layer) will be emitted per failure.
