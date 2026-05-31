## 1. Implement config change (cloud-provisioning)

- [x] 1.1 In `k8s/namespaces/zitadel/base/values.yaml`, add `InstanceHostHeaders: [x-zitadel-instance-host, x-zitadel-public-host]` under `zitadel.configmapConfig`, with a comment explaining the v4.7.1+ instance-host resolution + h2c `:authority` rationale (English only).
- [x] 1.2 Confirm no overlay (`overlays/dev`, `overlays/prod`) needs to override the new key (domain-independent → base only); leave overlays untouched.

## 2. Validate rendering locally

- [x] 2.1 Run `make lint-k8s` in `cloud-provisioning` (kustomize render + kube-linter) and confirm it passes.
- [x] 2.2 Render the prod overlay and confirm the `zitadel-api-config-yaml` ConfigMap contains `InstanceHostHeaders` with both `x-zitadel-instance-host` and `x-zitadel-public-host`.
- [x] 2.3 Confirm the rendered login `CUSTOM_REQUEST_HEADERS` and `ZITADEL_API_URL` are unchanged (chart-generated, not overridden).

## 3. Ship via GitOps

- [x] 3.1 Open a PR on `cloud-provisioning` (body explains the prod 504 / `Errors.Instance.NotFound` root cause; `Refs: #<issue>`).
- [x] 3.2 After all CI checks pass, merge to `main`.
- [x] 3.3 Confirm ArgoCD syncs the `zitadel` Application against the prod overlay.
- [x] 3.4 `kubectl -n zitadel rollout restart deploy/zitadel-api`; wait for the new pod to reach `2/2 Ready`.

## 4. Verify the fix in prod

- [x] 4.1 Load `https://auth.liverty-music.app/ui/v2/login/login` and confirm a non-5xx response (no Gateway 504).
- [x] 4.2 `gcloud logging read 'resource.labels.namespace_name="zitadel" AND jsonPayload.msg="unable to set instance"' --project=liverty-music-prod --freshness=1h` returns zero new entries after the restart.
- [x] 4.3 Confirm `zitadel-login` logs no `Failed to fetch security settings from API` on a fresh login load.
- [x] 4.4 Confirm browser→Gateway resolution still works (e.g., `/.well-known/openid-configuration` returns the discovery doc with the correct issuer).

## 5. Unblock downstream verification

- [x] 5.1 Complete an interactive sign-up via the hosted login UI and confirm it succeeds.

<!-- The PostHog `user.created` arrival check is out of scope here; it belongs to the
     analytics / user-creation-webhook change. AddHumanUser succeeding (code_0) confirms
     this fix unblocked it. -->

