## Context

Both use cases send their outcome signal through `sendSystemSignal` (`internal/usecase/analytics_client.go`). The searchers already return `apperr` errors with a code (`internal/infrastructure/gcp/gemini/errors.go` `toAppErr`), and the use cases wrap them with `fmt.Errorf("…: %w", err)`, which keeps the `*apperr.AppErr` reachable with `errors.As`.

## Goals / Non-Goals

**Goals:** count failed searches by cause in PostHog.

**Non-Goals:** telling an IAM denial from a spent spend cap. Both become `permission_denied`. Telling them apart would need a machine-readable reason in Gemini's error details, not a match on the message text; it is left until there is a need.

## Decisions

- **`error_code` is the `apperr` code's string** (`codes.Code.String()`, Connect's snake_case names such as `deadline_exceeded`), read from the first `*apperr.AppErr` in the error chain; an error without one reports `unknown`. Alternative: a new enum of search failure kinds. Rejected: it would duplicate the codes the searchers already choose and drift from them.
- **The message is not sent.** It can quote the official site's content or model output, and the signal's `trace_id` already leads to the full error in Cloud Logging.
- **HTTP 403 → PermissionDenied** in `toAppErr`, following AIP-193 (401 UNAUTHENTICATED, 403 PERMISSION_DENIED). Gemini's spend-cap response states `Status: PERMISSION_DENIED`. `isRetryable` keys on the HTTP status (401 retried, 403 not), so retries do not change.
- One helper in the usecase package (`errorCode(err) string`) serves both use cases.

## Risks / Trade-offs

- A caller that matched `Unauthenticated` for a Gemini 403 would change behavior. None does on main: the searchers' callers only test for an error; checked with `git grep` before implementing (task 1.1).
