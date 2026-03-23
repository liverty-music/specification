## Why

SearchNewConcerts RPC was changed to synchronous (waits for Gemini API completion before returning), but the timeout chain is misconfigured: GCP Backend Policy and HTTP HandlerTimeout are at 30s, while successful Gemini API calls take 16-25s and retries on 504 push total duration beyond 30s. This causes frequent 504 Gateway Timeout errors in both local and production environments.

Additionally, retrying on Gemini 504 (DEADLINE_EXCEEDED) is counterproductive — if Gemini itself timed out, an immediate retry is unlikely to succeed and wastes the remaining timeout budget.

## What Changes

- Unify timeout at 60s across the entire chain:
  - GCP Backend Policy `timeoutSec`: 30 → 60
  - Backend `SERVER_HANDLER_TIMEOUT`: 30s → 60s (ConfigMap)
- Extend pod termination chain to accommodate 60s requests:
  - `terminationGracePeriodSeconds`: 60 → 75
  - `SHUTDOWN_TIMEOUT`: 45s → 60s
- Remove redundant `context.WithTimeout(60s)` from `concert_uc.go` — HandlerTimeout already sets the context deadline
- Skip retry on Gemini 504 (DEADLINE_EXCEEDED) and 499 (CANCELLED) — treat as non-retryable

## Capabilities

### New Capabilities

None.

### Modified Capabilities

None. Infrastructure and retry logic adjustments only — no proto schema or requirement changes.

## Impact

- `cloud-provisioning/k8s/namespaces/backend/base/server/backend-policy.yaml` — LB timeout
- `cloud-provisioning/k8s/namespaces/backend/base/server/configmap.env` — HandlerTimeout, SHUTDOWN_TIMEOUT
- `cloud-provisioning/k8s/namespaces/backend/base/server/deployment.yaml` — terminationGracePeriodSeconds
- `backend/internal/usecase/concert_uc.go` — Remove context.WithTimeout
- `backend/internal/infrastructure/gcp/gemini/errors.go` — Remove 504/499 from retryable codes
- `backend/internal/infrastructure/gcp/gemini/errors_test.go` — Update test expectations
- HandlerTimeout 60s applies to all RPCs, but typical RPCs complete in a few hundred ms so no practical impact
