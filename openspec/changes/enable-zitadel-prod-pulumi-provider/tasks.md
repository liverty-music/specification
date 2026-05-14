## 1. Pre-flight verification

- [x] 1.1 Confirm `auth.liverty-music.app/.well-known/openid-configuration` returns 200 with `issuer: https://auth.liverty-music.app`: `curl -s https://auth.liverty-music.app/.well-known/openid-configuration | jq -r '.issuer'`. Verified 2026-05-14 — issuer returns `https://auth.liverty-music.app`.
- [x] 1.2 Confirm prod GSM has `zitadel-machine-key-for-pulumi-admin` with ≥1 enabled version: `gcloud secrets versions list zitadel-machine-key-for-pulumi-admin --project liverty-music-prod --filter='state=ENABLED'` returns ≥1 row. Verified — version 1 enabled at 2026-05-14T11:12:47Z.
- [x] 1.3 Confirm prod cluster's zitadel-api Pod is 3/3 Ready: `kubectl --context gke_liverty-music-prod_asia-northeast2_autopilot-cluster-osaka get pods -n zitadel -l app=zitadel,component=api`. Verified — Pod `zitadel-api-85d8666c65-6mvd6` 3/3 Running.
- [x] 1.4 Confirm Zitadel's "admin" org exists in prod by hitting the admin API once (curl test using the admin JWT) — verify the org id you'd get back via `zitadel.getOrg({ name: 'admin' })` will match what the bootstrap-uploaded JWT's `iss` claim points to (sanity check before relying on the data source). Verified via JWT-profile structure (`type: serviceaccount`, `keyId`, `userId`, `key` non-empty) — implicit org existence is confirmed by the JWT having been minted by Zitadel's first-boot bootstrap. The provider's data source lookup is tested at Pulumi preview time (§5.3) and confirmed: prod preview shows `zitadel.MachineUser` resource pinned to the resolved admin org id with no errors.

## 2. Extract `BackendMachineKeyComponent` (cloud-provisioning/src/zitadel/components/)

- [x] 2.1 Create `cloud-provisioning/src/zitadel/components/backend-machine-key.ts` defining `BackendMachineKeyComponent` (ComponentResource). Args: `{ env: 'dev' | 'prod', gcpProject: string, zitadelProvider: zitadel.Provider, orgId: pulumi.Input<string> }`. Outputs: the same `keyDetails: Output<string>` that the existing `MachineUserComponent` returns, plus the resulting GSM `Secret` + `SecretVersion` resource references. Done — also added optional `esoServiceAccountEmail` arg (defaults to `k8s-external-secrets@<gcpProject>.iam.gserviceaccount.com`) plus `secretAccessorBinding` output.
- [x] 2.2 Inside the new component, instantiate the existing `MachineUserComponent` (re-export from `./machine-user.js`) with the provided `orgId` + `zitadelProvider`. This re-uses the proven dev pattern verbatim. Done.
- [x] 2.3 Inside the new component, write the `MachineKey.keyDetails` to GSM via:
      - `new gcp.secretmanager.Secret('zitadel-machine-key-for-backend-app', ...)` (project from args, secretId = `zitadel-machine-key-for-backend-app`, auto replication)
      - `new gcp.secretmanager.SecretVersion(...)` (secretData = `MachineKey.keyDetails`, deletionPolicy DELETE)
      - `new gcp.secretmanager.SecretIamMember(...)` (role `secretAccessor`, member = the ESO GSA email `k8s-external-secrets@${gcpProject}.iam.gserviceaccount.com`)

      Done. Also added `labels: { env, managed_by: 'pulumi' }` on the Secret for parity with existing prod GSM conventions.
- [x] 2.4 ~~Apply `aliases: [{ name: 'OLD_URN' }]` to the `MachineKey` resource in `BackendMachineKeyComponent` for the dev URN to preserve dev state after refactor~~ — **SKIPPED**, no longer required. Implementation discovery during §2: dev's existing flow (`Zitadel` class → `MachineUserComponent` → `Gcp.SecretsComponent` writes `zitadel-machine-key-for-backend-app`) is left untouched. The new `BackendMachineKeyComponent` is **prod-only** at the call site (§4.1), so the dev URN tree is unaffected by definition — no aliases needed.

## 3. Refactor `Zitadel` class to use the extracted component (cloud-provisioning/src/zitadel/index.ts)

- [x] 3.1 ~~Replace the inline `new MachineUserComponent(...)` call inside the `Zitadel` class with a `new BackendMachineKeyComponent(...)` call. Keep the rest of `Zitadel` class behavior unchanged for dev.~~ — **SKIPPED** for zero-risk. Refactoring dev would have required moving `MachineUserComponent` under the new wrapper, changing all its child URNs (parent chain extension), and applying `aliases:` on three resources (MachineUser, MachineKey, OrgMember) to avoid Pulumi recreate-delete cycles. The design D1 goal — "a focused top-level component for prod's call site, avoiding the bloat of the full `Zitadel` class" — is fully achieved by `BackendMachineKeyComponent` being callable independently from `index.ts`. A future cleanup change can unify dev under the same component when there's a separate driver to do so (e.g., when dev refactor lands as part of right-size-prod or rotation work).
- [x] 3.2 ~~Verify `pulumi preview --stack dev` shows ZERO changes after the refactor~~ — **N/A** given §3.1 skip. §5.2 verified dev preview shows ONLY one unrelated `gcp:monitoring/dashboard:Dashboard` etag drift (pre-existing, not caused by this PR) plus 234 unchanged resources. Zero churn on any Zitadel/MachineKey/GSM resource.

## 4. Add prod call site (cloud-provisioning/src/index.ts)

- [x] 4.1 After the existing prod-enabled `SecretsComponent('zitadel-secrets', ...)` block at line ~119, add a NEW `env === 'prod'` block that:
      - Reads `zitadel-machine-key-for-pulumi-admin` GSM SecretVersion via `gcp.secretmanager.getSecretVersionAccessOutput({ project: 'liverty-music-prod', secret: 'zitadel-machine-key-for-pulumi-admin' })` (note: `getSecretVersionAccessOutput` returns `secretData`; the non-Access `getSecretVersion` returns only metadata).
      - Creates a `zitadel.Provider('zitadel-prod', { domain: 'auth.liverty-music.app', insecure: false, port: '443', jwtProfileJson })`
      - Looks up the existing "admin" org via `zitadel.getOrgsOutput({ name: 'admin', nameMethod: 'TEXT_QUERY_METHOD_EQUALS', state: 'ORG_STATE_ACTIVE' })` (see §4.2 for why `getOrgs` plural)
      - Instantiates `new BackendMachineKeyComponent('backend-app-prod', { env: 'prod', gcpProject: 'liverty-music-prod', zitadelProvider, orgId: adminOrgId, esoServiceAccountEmail: gcp.esoServiceAccountEmail })`

      Done at `src/index.ts:151-202`.
- [x] 4.2 Verify the `zitadel.getOrg` data source exists in the `@pulumiverse/zitadel` provider version pinned by `package.json`. If not, use `getOrgs` + filter. **Discovery**: `getOrg` (singular) requires `id`, NOT `name`. Used `getOrgsOutput` (plural) instead, which supports `name` + `nameMethod` query and returns `ids: string[]`. The runtime sanity check (§4.3) then asserts exactly one match.
- [x] 4.3 Add a runtime sanity check: `if (adminOrg.id is unknown OR returns empty) throw`. This catches the case where the data source lookup silently fails. Done — `adminOrgs.apply(...)` throws on `result.ids.length === 0` (clear "first-boot bootstrap didn't create the org" error) or `> 1` (refuse to guess; instructs operator to inspect Zitadel).

## 5. Local validation

- [x] 5.1 `make lint-ts` in cloud-provisioning — must pass after the refactor + new prod block. Done — biome + tsc pass. Required two fix-ups: (a) `import type` for `@pulumiverse/zitadel` in the new component (biome `useImportType`); (b) `"(ids: ${result.ids.join(', ')})"` was non-template (double-quoted) string with literal `${...}` — caught by `noTemplateCurlyInString`; converted to backtick template.
- [x] 5.2 `pulumi preview --stack dev` — expect ZERO changes (aliases preserve URN). **Result**: 234 unchanged + 1 unrelated update (`dashboard-zitadel-observability` etag drift; pre-existing dashboard server-side mutation, not caused by this PR). Zero changes to any Zitadel/MachineKey/GSM resource.
- [x] 5.3 `pulumi preview --stack prod` — expect ~5 resources to create: 1 `zitadel.MachineUser`, 1 `zitadel.MachineKey`, 1 `gcp.secretmanager.Secret`, 1 `gcp.secretmanager.SecretVersion`, 1 `gcp.secretmanager.SecretIamMember`. Plus parent ComponentResource. **Actual**: 9 resources to create — 6 backing resources (the 5 above + 1 `zitadel.OrgMember` for ORG_USER_MANAGER role which the design undercounted), plus 2 ComponentResources (parent `BackendMachineKey` + nested `MachineUser`) and 1 Zitadel `Provider`. All `(create)`; no replacements, no destroys. 202 unchanged.

## 6. PR preparation

- [ ] 6.1 Commit with Conventional Commits: `feat(infra): enable Zitadel prod Pulumi provider + backend MachineKey creation`.
- [ ] 6.2 Open PR in `cloud-provisioning` referencing this OpenSpec change.
- [ ] 6.3 Open companion PR in `specification` with this OpenSpec change task ticks.
- [ ] 6.4 Wait for Pulumi Cloud auto-preview on both stacks: dev shows the same single Dashboard etag drift; prod shows the expected 9-resource creation.
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
