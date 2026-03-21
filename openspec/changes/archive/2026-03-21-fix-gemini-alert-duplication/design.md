## Context

The Gemini concert searcher (`internal/infrastructure/gcp/gemini/searcher.go`) logs at ERROR when the API call fails, and the calling usecase (`internal/usecase/concert_uc.go`) also logs at ERROR when the search fails. Both logs match the `severity="ERROR"` filter in the Cloud Monitoring alert policy.

Cloud Monitoring's `conditionMatchedLog` with `labelExtractors` creates separate incidents when extracted label values differ. The infrastructure-layer log has `jsonPayload.error` as a plain string (no `.code` sub-field), while the usecase-layer log has `jsonPayload.error.code` as a structured field. This causes `error_code` to extract differently (empty vs `"unauthenticated"`), resulting in two incidents from one failure.

Separately, GKE Workload Identity token refresh can intermittently produce HTTP 401 errors. The current `isRetryable` function treats 401 as permanent, so the backoff loop exits immediately instead of retrying.

## Goals / Non-Goals

**Goals:**
- Eliminate duplicate alert incidents caused by multi-layer ERROR logging of the same failure.
- Make transient WI credential failures recoverable via the existing retry mechanism.

**Non-Goals:**
- Changing the Cloud Monitoring alert policy configuration or `labelExtractors`.
- Changing log structure or fields.
- Addressing other error types or retry behaviors.

## Decisions

### 1. Demote infrastructure-layer log to WARN

**Change**: `searcher.go:227` — `s.logger.Error(...)` → `s.logger.Warn(...)`

**Rationale**: The infrastructure layer provides detailed context (model version, artist, official site) which is valuable for debugging but should not independently trigger alerts. The usecase layer is the appropriate place for ERROR-level logging because it has the full business context (artist_id) and wraps the error with `apperr` which populates `error.code`.

**Alternative considered**: Filter the alert policy by `jsonPayload.msg` to only match usecase-layer messages. Rejected because it couples the alert policy to specific log message strings, making it fragile.

### 2. Add HTTP 401 to `isRetryable`

**Change**: Add `http.StatusUnauthorized` (401) to the switch in `errors.go:isRetryable`.

**Rationale**: WI token refresh failures are transient (typically resolve within seconds). The existing backoff configuration (1s initial, 2x multiplier, max 10s, 3 tries) is well-suited to handle this. A 401 from Vertex AI in a GKE environment with Workload Identity is almost always a transient credential issue, not a genuine authorization failure.

**Alternative considered**: Only retry 401 when a specific error detail (`CREDENTIALS_MISSING`) is present. Rejected because the `genai.APIError` type only exposes the HTTP status code, not the detailed error reason. Parsing the error message string would be fragile.

## Risks / Trade-offs

- **[Risk] Retrying genuine 401 errors**: If the service account truly lacks `aiplatform.user` permissions, the retry will fail 3 times before giving up (adding ~7s latency). → **Mitigation**: The 3-retry cap with exponential backoff limits the blast radius. Genuine permission errors will still surface as ERROR in the usecase layer after retries are exhausted.
- **[Risk] WARN logs are less visible**: Operators may miss infrastructure-level details when triaging. → **Mitigation**: The usecase-layer ERROR log includes the full wrapped error with cause chain. Cloud Logging correlation via `trace_id` allows finding the WARN log for additional context.
