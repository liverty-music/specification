## 1. Cloud Provisioning — Timeout & Termination Chain

- [x] 1.1 Change `timeoutSec` from 30 to 60 in `k8s/namespaces/backend/base/server/backend-policy.yaml`
- [x] 1.2 Set `SERVER_HANDLER_TIMEOUT=60s` in `k8s/namespaces/backend/base/server/configmap.env`
- [x] 1.3 Update `SHUTDOWN_TIMEOUT` from 45s to 60s in `k8s/namespaces/backend/base/server/configmap.env`, update the formula comment to reflect `terminationGracePeriodSeconds(75) - preStop(5) - buffer(10) = 60s`
- [x] 1.4 Change `terminationGracePeriodSeconds` from 60 to 75 in `k8s/namespaces/backend/base/server/deployment.yaml`
- [x] 1.5 Validate K8s manifests with Kustomize dry-run

## 2. Backend — Remove Redundant Timeout & Fix Retry

- [x] 2.1 Remove `context.WithTimeout(ctx, 60*time.Second)` from `concert_uc.go:268` — pass caller's `ctx` directly to `concertSearcher.Search()`
- [x] 2.2 Remove 504 (`http.StatusGatewayTimeout`) and 499 from `isRetryable()` in `gemini/errors.go` — update the doc comment to explain why these are non-retryable
- [x] 2.3 Update `gemini/errors_test.go` to expect `isRetryable(504) == false` and `isRetryable(499) == false`
- [x] 2.4 Run `make check` in backend repo

## 3. PR & Verification

- [x] 3.1 Create cloud-provisioning PR #174, CI pass, merged
- [x] 3.2 Create backend PR #252, CI pass, merged
- [x] 3.3 ArgoCD sync confirmed, pod rollout complete (server-app-65c5b4559c-shfwj)
- [x] 3.4 Verified: 宇多田ヒカル follow → SearchNewConcerts status: ok, duration_ms: 21055, no 504
