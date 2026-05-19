## 1. Pulumi: System User key generation + GSM Secret

- [x] 1.1 Add `@pulumi/tls` to `cloud-provisioning/package.json`. In `cloud-provisioning/src/zitadel/components/secrets.ts` (extend `SecretsComponent`), add a `tls.PrivateKey` resource named `zitadel-system-api-key` (`algorithm: "RSA"`, `rsaBits: 2048`). Pulumi state persists the generated key, making the pair idempotent across re-applies. Export `systemApiPrivateKeyPem` (`pulumi.Output<string>`, `pulumi.secret`-wrapped) and `systemApiPublicKeyPem` (`pulumi.Output<string>`) from the component.
- [x] 1.2 Add `gcp.secretmanager.Secret` named `zitadel-system-api-key` (PreservedTier — mirror `zitadel-masterkey` posture in `secrets.ts`) plus a `gcp.secretmanager.SecretVersion` carrying the **private** key PEM. Add a sibling `gcp.secretmanager.Secret` `zitadel-system-api-pub` for the **public** key PEM so ESO can sync it into the cluster without exposing the private half. Add ESO read bindings for the cluster ESO SA on the public Secret (analogous to `zitadel-masterkey-eso-accessor`).
- [ ] 1.3 Confirm the new GSM Secrets are created in both `liverty-music-dev` and `liverty-music-prod` projects via `pulumi preview -s dev` and `pulumi preview -s prod`. Confirm no destructive operations are flagged on existing Zitadel resources.

## 2. K8s: deliver public key to `zitadel-api` Pod

- [x] 2.1 Add `ExternalSecret` (file `cloud-provisioning/k8s/namespaces/zitadel/base/external-secret-system-api-pub.yaml`) syncing the **public** key from GSM Secret `zitadel-system-api-pub` into a K8s Secret `zitadel-system-api-pub`. Project the public key at a stable path (e.g. `/var/run/zitadel/system-api/pulumi-system.pem`).
- [x] 2.2 Patch `cloud-provisioning/k8s/namespaces/zitadel/base/deployment-api.yaml` to mount the projected public key and to set `ZITADEL_SYSTEMAPIUSERS` env using the JSON form: `{"pulumi-system":{"Path":"/var/run/zitadel/system-api/pulumi-system.pem"}}`. Keep the existing `reloader.stakater.com/auto: "true"` annotation so secret rotation triggers a rollout.
- [x] 2.3 Add `external-secret-system-api-pub.yaml` to `cloud-provisioning/k8s/namespaces/zitadel/base/kustomization.yaml` resources list. Render the dev and prod overlays (`make lint-k8s`) and confirm the env var + volume mount appear in both, the prod overlay does not need a divergent value (the System User name is environment-agnostic), and no other env keys are perturbed.
- [ ] 2.4 Apply via ArgoCD on dev. Verify `zitadel-api` Pods restart cleanly, `/debug/ready` returns 200 within the same SLO as before, and Pod logs contain no "Failed to load SystemAPIUsers" / "could not parse PEM" errors.

## 3. Pulumi Dynamic Resource: `ZitadelInstanceCustomDomain`

- [x] 3.1 Extend [`cloud-provisioning/src/zitadel/dynamic/api-client.ts`](cloud-provisioning/src/zitadel/dynamic/api-client.ts) with `buildSystemAssertion(profile, audience)`. Mirror existing `buildAssertion` but use `iss = sub = profile.userName` and emit a JWT to be sent **directly as Bearer** (no `/oauth/v2/token` exchange). Add a `callSystemApi(domain, profile, path, body)` helper that POSTs to `https://${domain}${path}` with `Authorization: Bearer <JWT>` and `Content-Type: application/json`, returning the parsed JSON response. Use only Node built-ins (`crypto`, `https`, `url`) per the file's existing serialization constraint.
- [x] 3.2 Create `cloud-provisioning/src/zitadel/dynamic/instance-custom-domain.ts` exporting `ZitadelInstanceCustomDomain` Pulumi Dynamic Resource. CRUD callbacks:
  - **create**: call `POST /zitadel.instance.v2.InstanceService/AddCustomDomain` with body `{ instanceId, customDomain }`. Persist `{ instanceId, customDomain }` as the resource id.
  - **read** (`diff`/`check`): call `POST /zitadel.instance.v2.InstanceService/ListCustomDomains` and confirm the `customDomain` is present.
  - **delete**: call `POST /zitadel.instance.v2.InstanceService/RemoveCustomDomain` with body `{ instanceId, customDomain }`.
  - Treat "already exists" responses on create as success (idempotent).
- [x] 3.3 Wire export in [`cloud-provisioning/src/zitadel/dynamic/index.ts`](cloud-provisioning/src/zitadel/dynamic/index.ts).
- [x] 3.4 Add unit tests under `cloud-provisioning/src/zitadel/dynamic/__tests__/instance-custom-domain.test.ts` covering: JWT signing shape (header alg/typ, payload iss/sub/aud/exp/iat), idempotency on `AlreadyExists` reply, 401/403 surfaced with actionable message, list-paging tolerance.

## 4. Pulumi: declare the InstanceCustomDomain per environment

- [x] 4.1 `instanceIdMap: Record<Environment, string>` added to `src/zitadel/constants.ts` with `__UNSET__` placeholders + a doc comment describing the discovery procedure. `scripts/discover-zitadel-instance-id.mjs` (helper) calls `instance.v2.InstanceService/ListInstances` with a Pulumi-system-signed JWT after fetching the private key from GSM, and prints the id ready to paste. (Phase 2 will commit the real ids.)
- [ ] 4.2 In `src/index.ts`, instantiate `new ZitadelInstanceCustomDomain('zitadel-api-internal', { domain: zitadelDomainMap[env], systemUserName: SYSTEM_API_USER_NAME, privateKeyPem: zitadelSecrets.systemApiPrivateKeyPem, instanceId: instanceIdMap[env], customDomain: ZITADEL_API_INTERNAL_HOST }, { dependsOn: [zitadelSecrets.systemApiPrivateSecretVersion] })`, gated on `workloadEnabled && zitadel !== undefined`. **Phase 2** — implementation already drafted and removed from Phase 1 commit; re-apply from this task's description after Phase 1 lands and `instanceIdMap` is populated.
- [ ] 4.3 Run `pulumi preview` on dev; confirm the only Created resources are the System User key Secrets/Versions + ExternalSecret + Dynamic Resource. No replacements on existing resources, no surprise Reads.
- [ ] 4.4 Apply on dev (via Pulumi Cloud Deployment on merge to main). Confirm via `wget --post-data='{"instanceId":"<id>"}' https://auth.dev.liverty-music.app/zitadel.instance.v2.InstanceService/ListCustomDomains` (with a System User JWT or `pulumi-admin` PAT) that the new domain is present.
- [ ] 4.5 Smoke test from `zitadel-web` Pod (read-only, no PAT exposure): `wget -O- http://zitadel-api.zitadel.svc.cluster.local:8080/.well-known/openid-configuration` returns 200 with a body whose `issuer` matches the env's public URL.

## 5. K8s: flip `ZITADEL_API_URL` on `zitadel-web` (**Phase 2**)

> Gate per 5.4 below: this section lands in a **second PR** after Phase 1
> (sections 1–4 minus 4.1) has been applied on both envs and the
> instance ids have been captured into `instanceIdMap`.

- [ ] 5.1 Update [`cloud-provisioning/k8s/namespaces/zitadel/base/deployment-web.yaml`](cloud-provisioning/k8s/namespaces/zitadel/base/deployment-web.yaml) so `ZITADEL_API_URL` reads `http://zitadel-api.zitadel.svc.cluster.local:8080`. Rewrite the surrounding comment block (lines 60–82) to record the hairpin incident root cause, the new cluster-internal path, and the link to this change. *(Implementation already drafted and proven via `kubectl kustomize` in the Phase 1 worktree; the diff was reverted from Phase 1 to keep the URL flip in Phase 2 per gate decision.)*
- [ ] 5.2 Update [`cloud-provisioning/k8s/namespaces/zitadel/overlays/prod/deployment-web-patch.yaml`](cloud-provisioning/k8s/namespaces/zitadel/overlays/prod/deployment-web-patch.yaml) to drop the env-var override for `ZITADEL_API_URL` (the cluster-internal value is identical across envs). Update the patch comment accordingly.
- [ ] 5.3 Render both overlays (`make lint-k8s`) and confirm the env value is the cluster-internal URL in both dev and prod outputs.
- [x] 5.4 **Gate decision — option (a): two-PR split**. Phase 1 PR lands sections 1.1–1.2, 2.1–2.3, 3.1–3.4, plus the `instanceIdMap` placeholders and the `scripts/discover-zitadel-instance-id.mjs` helper. After Phase 1's dev auto-apply lands and the `zitadel-api` Pod has rolled with the new env, run `node scripts/discover-zitadel-instance-id.mjs --env=dev` (and `--env=prod` after prod apply) and commit the captured ids into `instanceIdMap`. Phase 2 PR then completes sections 4.2, 5.1–5.3 (wire up `ZitadelInstanceCustomDomain` in `src/index.ts` and flip `ZITADEL_API_URL`). This sequence prevents the Dynamic Resource's first `create` callback from racing the API Pod rollout (Pulumi cannot track Pod rollout — that's ArgoCD's plane).

## 6. Verification

- [ ] 6.1 In dev: re-run the reproducer — request `https://auth.dev.liverty-music.app/oauth/v2/authorize?...&prompt=create` from outside, follow the redirect to `/ui/v2/login/login?authRequest=V2_xxx`, confirm the response is **not** 504 and TTFB is well under 30s. Verify the dispatcher redirects (302) onward to the appropriate page (`/loginname`, `/register`, etc.).
- [ ] 6.2 In dev: confirm `zitadel-web` Pod logs no longer show repeated `fetch() returned undefined` middleware errors (verify the iframe-CSP fallback log is gone — confirms successful API calls).
- [ ] 6.3 In dev: complete a full sign-up flow with a fresh email via the Pixel-class user-agent that originally exposed the bug. Capture HAR and attach to PR.
- [ ] 6.4 Repeat 6.1–6.3 against prod after the prod manual Pulumi apply.
- [ ] 6.5 Confirm no regression on existing flows: `auth.<env>.liverty-music.app/.well-known/openid-configuration` from outside still returns 200; backend service can still mint a JWT via the existing `pulumi-admin` Machine Key (existing E2E suite passes).

## 7. Spec sync + archive prep

- [ ] 7.1 Update the runbook(s) under `cloud-provisioning/docs/runbooks/` that reference the prior public-URL design (search for `ZITADEL_API_URL`, `auth.dev.liverty-music.app`, `hairpin`).
- [ ] 7.2 Update `cloud-provisioning/docs/DEV_VS_PROD_DIFFERENCES.md` if the new System User or InstanceCustomDomain row deserves listing.
- [ ] 7.3 Mark all tasks in this file as complete and run `openspec validate route-login-v2-via-internal-zitadel-api` from the specification repo.
- [ ] 7.4 Archive the change via `/opsx:archive` once both environments are verified per section 6.
