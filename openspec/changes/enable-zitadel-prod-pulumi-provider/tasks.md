## 1. Pre-flight verification

- [ ] 1.1 Confirm `auth.liverty-music.app/.well-known/openid-configuration` returns 200 with `issuer: https://auth.liverty-music.app`: `curl -s https://auth.liverty-music.app/.well-known/openid-configuration | jq -r '.issuer'`
- [ ] 1.2 Confirm prod GSM has `zitadel-machine-key-for-pulumi-admin` with ≥1 enabled version: `gcloud secrets versions list zitadel-machine-key-for-pulumi-admin --project liverty-music-prod --filter='state=ENABLED'` returns ≥1 row
- [ ] 1.3 Confirm prod cluster's zitadel-api Pod is 3/3 Ready: `kubectl --context gke_liverty-music-prod_asia-northeast2_autopilot-cluster-osaka get pods -n zitadel -l app=zitadel,component=api`
- [ ] 1.4 Confirm Zitadel's "admin" org exists in prod by hitting the admin API once (curl test using the admin JWT) — verify the org id you'd get back via `zitadel.getOrg({ name: 'admin' })` will match what the bootstrap-uploaded JWT's `iss` claim points to (sanity check before relying on the data source).

## 2. Extract `BackendMachineKeyComponent` (cloud-provisioning/src/zitadel/components/)

- [ ] 2.1 Create `cloud-provisioning/src/zitadel/components/backend-machine-key.ts` defining `BackendMachineKeyComponent` (ComponentResource). Args: `{ env: 'dev' | 'prod', gcpProject: string, zitadelProvider: zitadel.Provider, orgId: pulumi.Input<string> }`. Outputs: the same `keyDetails: Output<string>` that the existing `MachineUserComponent` returns, plus the resulting GSM `Secret` + `SecretVersion` resource references.
- [ ] 2.2 Inside the new component, instantiate the existing `MachineUserComponent` (re-export from `./machine-user.js`) with the provided `orgId` + `zitadelProvider`. This re-uses the proven dev pattern verbatim.
- [ ] 2.3 Inside the new component, write the `MachineKey.keyDetails` to GSM via:
      - `new gcp.secretmanager.Secret('zitadel-machine-key-for-backend-app', ...)` (project from args, secretId = `zitadel-machine-key-for-backend-app`, auto replication)
      - `new gcp.secretmanager.SecretVersion(...)` (secretData = `MachineKey.keyDetails`, deletionPolicy DELETE)
      - `new gcp.secretmanager.SecretIamMember(...)` (role `secretAccessor`, member = the ESO GSA email `k8s-external-secrets@${gcpProject}.iam.gserviceaccount.com`)
- [ ] 2.4 Apply `aliases: [{ name: 'OLD_URN' }]` to the `MachineKey` resource in `BackendMachineKeyComponent` for the dev URN to preserve dev state after refactor — capture the current dev URN via `pulumi stack export --stack dev | jq '.deployment.resources[] | select(.type == "zitadel:index/machineKey:MachineKey")'`.

## 3. Refactor `Zitadel` class to use the extracted component (cloud-provisioning/src/zitadel/index.ts)

- [ ] 3.1 Replace the inline `new MachineUserComponent(...)` call inside the `Zitadel` class with a `new BackendMachineKeyComponent(...)` call. Keep the rest of `Zitadel` class behavior unchanged for dev.
- [ ] 3.2 Verify `pulumi preview --stack dev` shows ZERO changes after the refactor (the `aliases:` move should be state-only — no resource recreation). If it shows replacement of the `MachineKey`, abort and fix the alias URN.

## 4. Add prod call site (cloud-provisioning/src/index.ts)

- [ ] 4.1 After the existing prod-enabled `SecretsComponent('zitadel-secrets', ...)` block at line ~119, add a NEW `env === 'prod'` block that:
      - Reads `zitadel-machine-key-for-pulumi-admin` GSM SecretVersion via `gcp.secretmanager.getSecretVersion({ project: 'liverty-music-prod', secret: 'zitadel-machine-key-for-pulumi-admin' })`
      - Creates a `zitadel.Provider('zitadel-prod', { domain: 'auth.liverty-music.app', jwtProfileJson })`
      - Looks up the existing "admin" org via `zitadel.getOrg({ name: 'admin' }, { provider: zitadelProdProvider })`
      - Instantiates `new BackendMachineKeyComponent('backend-app', { env: 'prod', gcpProject: 'liverty-music-prod', zitadelProvider, orgId: adminOrg.id })`
- [ ] 4.2 Verify the `zitadel.getOrg` data source exists in the `@pulumiverse/zitadel` provider version pinned by `package.json`. If not, use `getOrgs` + filter (or fall back to passing the org id via a Pulumi config — least desirable).
- [ ] 4.3 Add a runtime sanity check: `if (adminOrg.id is unknown OR returns empty) throw`. This catches the case where the data source lookup silently fails.

## 5. Local validation

- [ ] 5.1 `make lint-ts` in cloud-provisioning — must pass after the refactor + new prod block.
- [ ] 5.2 `pulumi preview --stack dev` — expect ZERO changes (aliases preserve URN).
- [ ] 5.3 `pulumi preview --stack prod` — expect ~5 resources to create: 1 `zitadel.MachineUser`, 1 `zitadel.MachineKey`, 1 `gcp.secretmanager.Secret`, 1 `gcp.secretmanager.SecretVersion`, 1 `gcp.secretmanager.SecretIamMember`. Plus parent ComponentResource.

## 6. PR preparation

- [ ] 6.1 Commit with Conventional Commits: `feat(infra): enable Zitadel prod Pulumi provider + backend MachineKey creation`.
- [ ] 6.2 Open PR in `cloud-provisioning` referencing this OpenSpec change.
- [ ] 6.3 Open companion PR in `specification` with this OpenSpec change (proposal + design + specs delta + tasks).
- [ ] 6.4 Wait for Pulumi Cloud auto-preview on both stacks: dev shows zero changes; prod shows the expected ~5-resource creation.
- [ ] 6.5 Wait for reviewer approval. Given this affects prod (creates Zitadel API objects + new GSM Secret), require explicit "approved" comment.

## 7. Prod deployment (manual, after PR merge)

- [ ] 7.1 Trigger `pulumi up --stack prod` from Pulumi Cloud console.
- [ ] 7.2 Verify the prod-side resources created: `gcloud secrets versions list zitadel-machine-key-for-backend-app --project liverty-music-prod` returns ≥1 enabled version.
- [ ] 7.3 ESO reconciles the new GSM SecretVersion to the backend namespace's K8s Secret within ~30s.
- [ ] 7.4 Reloader picks up the new K8s Secret and rolls the backend Deployment.
- [ ] 7.5 Backend Pods (`server-app`, `consumer-app`) transition from `ContainerCreating` to `Running`.
- [ ] 7.6 Verify backend → Zitadel auth path is live: `curl -I https://api.liverty-music.app/grpc.health.v1.Health/Check` returns 200 (this exercises the gRPC health endpoint which is auth-exempt; for an auth-bearing test, hit any RPC that calls Zitadel, e.g. user info read).

## 8. Archive

- [ ] 8.1 Update this tasks.md + design.md with any incident notes from the live bootstrap (Pulumi-up duration, any data-source lookup quirks, observed backend Pod sync time).
- [ ] 8.2 Run `openspec validate enable-zitadel-prod-pulumi-provider --strict`.
- [ ] 8.3 Sync delta specs to main specs (`openspec/specs/zitadel-self-hosted-deployment/spec.md` — apply MODIFIED + ADDED operations).
- [ ] 8.4 Move change directory: `git mv openspec/changes/enable-zitadel-prod-pulumi-provider openspec/changes/archive/YYYY-MM-DD-enable-zitadel-prod-pulumi-provider`.
- [ ] 8.5 Commit + push + merge the archive PR.
- [ ] 8.6 Now that backend is up, also archive the `prod-k8s-manifests` change (open its archive PR — it was deferred until backend reached Healthy).
