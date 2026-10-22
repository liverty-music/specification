## 1. Resend through the event consumer (backend)

- [ ] 1.1 Add the `USER.email_verification_resend_requested` subject and `{user_id}` payload with json tags in `internal/entity/event_data.go`; verify `make check`
- [ ] 1.2 Change `UserUseCase.ResendEmailVerification` to resolve the caller, apply the existing limiter, and publish the announcement (Unavailable on publish failure); verify unit tests for components/usecase/user/resend-email-verification "Too many requests", "Failed attempts count", "Limit is per user", "Caller resends their own email", "Caller already verified", "Email verification not configured", "Announcement fails"
- [ ] 1.3 Implement `UserUseCase.ReissueEmailVerification` and register the `reissue-email-verification` consumer handler on the USER stream; verify unit tests for components/usecase/user/reissue-email-verification "Unverified address", "Already verified", "Account deleted since the request", "Verification not configured", "Identity provider down"
- [ ] 1.4 Log at startup which identity-provider clients DI built (none, verifier, remover), so the fan API's lack of a key is visible; verify a DI test with the key path unset builds neither and the fan handlers still register

## 2. Deployment (cloud-provisioning)

- [ ] 2.1 Add a KEDA `nats-jetstream` trigger for the `reissue-email-verification` consumer on the USER stream in `event-consumer/scaledobject.yaml`; verify `kubectl kustomize` output for the prod overlay
- [ ] 2.2 Remove the `zitadel-machine-key-for-backend-app.json` entry from `fan-api/external-secret.yaml` and its volume, mount and env var from the `fan-api` Deployment (keep them on `event-consumer` and `admin-console-api`); verify `kubectl kustomize` for prod shows no Zitadel key on `fan-api` and unchanged mounts on the other two
- [ ] 2.3 After backend 1.x is deployed, merge 2.x and roll out to prod; verify `kubectl exec` into a `fan-api` Pod finds no `/secrets/zitadel` and its startup log reports no identity-provider clients, quoting both outputs

## 3. Prod verification

- [ ] 3.1 Confirm a resend request handled in prod: either trigger one from Settings with an unverified account, or quote the `reissue-email-verification` handler log of the next real request together with the consumer's ack; record the evidence under the @spec-manual lines below

@spec-manual components/infrastructure/fan/api/server/identity-provider-credentials "Fan API deployment" -- task 2.3 (`kubectl exec` and startup log in prod)
@spec-manual components/infrastructure/fan/api/server/identity-provider-credentials "Fan requests a verification resend" -- task 3.1
@spec-manual components/infrastructure/fan/api/server/identity-provider-credentials "Signed-in calls keep working" -- after task 2.3, a signed-in prod call (e.g. Settings load) succeeds and fan-api logs show no Unauthenticated spike
