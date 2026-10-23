## 1. Proto and naming rule (specification)

- [x] 1.1 Add `proto/liverty_music/rpc/backend/user/v1/user_service.proto` (`UserService`: `SendEmailVerification`, `ResendEmailVerification`, `IssuePasskeyRegistrationLink`, `DeleteIdentity`) and `rpc/backend/organization/v1/organization_service.proto` (`OrganizationService` with the five Organization operations of design D2, names fixed against the `rpc-design` skill). Use wrapper types and protovalidate, and doc comments that say each service is cluster-internal and lists its error codes. Verify `make check` and `buf breaking` pass in CI
- [x] 1.2 Add the `backend` caller to the `rpc-design` skill rule "Packages name the caller" (`.claude/skills/rpc-design/SKILL.md:16`) and to the review criteria in `AGENTS.md`; verify `make words` passes
- [x] 1.3 Merge, publish a GitHub Release and confirm `buf-release.yml` succeeded (`gh run list --repo liverty-music/specification --workflow buf-release.yml --limit 3`)

## 2. Identity binary (backend)

- [x] 2.1 Consume the released schema (`consume-proto-release` skill); verify `make check`
- [x] 2.2 Add `cmd/identity` and its DI: the four existing Zitadel clients and token sources, no database or NATS, and a config with the three key paths and the listener ports (design D1, D5). Verify a DI test that it builds and starts without a database
- [x] 2.3 Implement the internal `UserService` and `OrganizationService` handlers on the existing Zitadel clients. Keep today's error codes (NotFound, FailedPrecondition for an unverified email, Unavailable) and never log the passkey link or code. Verify handler tests per procedure against a fake identity provider
- [x] 2.4 Serve one listener per caller (9100 event consumer, 9101 admin console API), each with a deny-by-default procedure allowlist interceptor (design D3). Verify tests for components/infrastructure/backend/process/identity-provider-credentials "Operation outside the caller's set" (consumer listener refuses `DeleteIdentity` with PermissionDenied, nothing called), plus one allowed call per listener
- [x] 2.5 Add gRPC health on 8080: liveness is the process, readiness is listeners up and not shutting down, with no database or identity-provider check (spec health-probes). Verify tests for components/infrastructure/backend/process/health-probes "Identity provider unreachable" and "Identity service shutting down"
- [x] 2.6 Add the `identity` Dockerfile stage (distroless static nonroot) and the image in `docker-bake.hcl`, the `IMAGES` list in `deploy.yml`, the release copy matrix and `dispatch-prod-pin` (design D7); verify `docker buildx bake identity` locally and the push-path run builds `backend/identity` in CI

## 3. Callers (backend)

- [x] 3.1 Add `internal/infrastructure/identity`, implementing `EmailVerifier`, `PasskeyRegistrationLinkIssuer`, `IdentityRemover` and `OrganizationRepository` over the internal RPCs with h2c. Map Connect codes back to the same `apperr` codes. Verify client tests with a fake server for each method and each error code, including components/infrastructure/backend/process/identity-provider-credentials "Fan requests a verification resend" (the consumer's `ReissueEmailVerification` path calls `ResendEmailVerification`) and "Admin deletes a fan" (the admin `DeleteIdentity` path calls the identity service)
- [x] 3.2 Wire `IDENTITY_SERVICE_URL` on the event consumer and the admin console API: set → identity client; unset in local → today's no-op and unavailable fallbacks; unset outside local → today's direct client (design D4). Verify DI tests for the three cases and `make check`
- [x] 3.3 Confirm whether the admin console API's `EmailVerifier` (`provider.go:126-145`) has any caller. If none, stop building it; verify `make check`
- [x] 3.4 Merge, cut the backend Release after the push-path image is built, and confirm `backend/identity:<version>` exists in prod AR

## 4. Cluster (cloud-provisioning)

- [x] 4.1 Add ExternalSecret `identity-secrets` with the three GSM keys (ESO-only access), Deployment `identity` (one replica, its own KSA `identity` with no GSA (design D5), probes on 8080, the three key mounts and path variables) and Service `identity` (ClusterIP, ports 9100 and 9101, no Gateway route), pinned to the release of 3.4. Set `IDENTITY_SERVICE_URL` on `event-consumer` and `admin-console-api`, which keep their keys for now. Verify `kubectl kustomize` of the prod and dev overlays and `make lint-k8s`
- [x] 4.2 Add NetworkPolicy `identity-ingress`: TCP 9100 from `app=event-consumer`, TCP 9101 from `app=admin-console-api`, 8080 for probes, everything else denied (design D3). Verify `kubectl kustomize` shows it and `make lint-k8s`
- [x] 4.3 After merge, check in prod and quote the output:
  - `identity` is Ready;
  - a sign-up verification or Settings resend and a passkey recovery link go through identity (identity logs);
  - an admin action that reads or changes an Organization goes through identity;
  - `kubectl run` with a pod labelled anything else cannot connect to `identity:9100` or `identity:9101`.

## 5. Remove the old paths (backend, cloud-provisioning)

- [x] 5.1 Remove the direct-client fallback and the three key-path settings from the consumer and admin console API configs (design D4); verify `make check` and a DI test that both fail to start outside local without `IDENTITY_SERVICE_URL`. Merge and release
- [x] 5.2 After that release is in prod, unmount the keys and their path variables from `event-consumer` and `admin-console-api` and drop the keys from `event-consumer-secrets` and the admin secrets. Verify `kubectl kustomize` shows the key volumes only on `identity`, and in prod `kubectl get deploy event-consumer admin-console-api -o yaml` lists no Zitadel key volume or variable
- [x] 5.3 At archive, edit the Purpose of `openspec/specs/components/infrastructure/backend/process/identity-provider-credentials/spec.md` to say only the identity service holds a credential

@spec-manual components/infrastructure/backend/process/identity-provider-credentials "API server deployment" -- task 5.2 (prod `kubectl get deploy -o yaml` for every API workload and the consumer shows no Zitadel key volume or variable)
@spec-manual components/infrastructure/backend/process/identity-provider-credentials "Process with no access" -- task 4.3 (`kubectl run` client without an allowed label cannot connect to 9100 or 9101; the fan API has no allowed label)
@spec-manual components/infrastructure/backend/process/identity-provider-credentials "Request from outside the cluster" -- task 4.1/4.3 (Service `identity` is ClusterIP with no Gateway route; `curl` from outside to the auth and API hosts has no path to it)
@spec-manual components/infrastructure/backend/process/identity-provider-credentials "Signed-in calls keep working" -- task 4.3 (signed-in fan, organizer and reception calls succeed in prod after the switch)
