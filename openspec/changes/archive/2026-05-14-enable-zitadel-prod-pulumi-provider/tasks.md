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

- [x] 6.1 Commit with Conventional Commits: `feat(infra): enable Zitadel prod Pulumi provider + backend MachineKey creation`. cloud-provisioning PR #257 (final merge commit 47b1b47).
- [x] 6.2 Open PR in `cloud-provisioning` referencing this OpenSpec change. https://github.com/liverty-music/cloud-provisioning/pull/257.
- [x] 6.3 Open companion PR in `specification` with this OpenSpec change task ticks. https://github.com/liverty-music/specification/pull/465 (merged at b18b3be).
- [x] 6.4 Wait for Pulumi Cloud auto-preview on both stacks: dev shows the same single Dashboard etag drift; prod shows the expected creation set. Verified — prod preview settled at 10 resources to create after the round-3 productOrg fix (one more than the original design — see §5.3 note).
- [x] 6.5 Wait for reviewer approval. **Review surfaced three real bugs across 3 rounds**: (round-1) `MachineUser.keyDetails` → `MachineKey.keyDetails` typo; (round-2) `pulumi.secret()` wraps missing on admin JWT + backend MachineKey, `index.ts` orchestration logic violating the thin-dispatch principle (per CLAUDE.md), hardcoded `auth.liverty-music.app` not using `zitadelDomainMap[env]`; (round-3) **privilege-escalation** — original D2 placed backend-app in admin org with `ORG_USER_MANAGER`, giving it user-management authority over operator identities (pulumi-admin, login-client, human IAM_OWNERs). Fixed by creating a separate `productOrg` for backend-app. Round-4 CI: zero new comments; both PRs merged.

## 7. Prod deployment (manual, after PR merge)

- [x] 7.1 Trigger `pulumi up --stack prod` from Pulumi Cloud console. Done 2026-05-14T14:58 UTC.
- [x] 7.2 Verify the prod-side resources created: `gcloud secrets versions list zitadel-machine-key-for-backend-app --project liverty-music-prod` returns ≥1 enabled version. Verified — v1 enabled at 2026-05-14T14:59:40Z.
- [x] 7.3 ESO reconciles the new GSM SecretVersion to the backend namespace's K8s Secret within ~30s. **Required a manual `kubectl annotate force-sync=now` to trigger early reconcile** — ESO's first reconcile attempt failed before the GSM Secret existed and the next retry was scheduled per the 1h refresh interval. After force-sync, K8s Secret `backend-secrets` populated within ~5s.
- [x] 7.4 Reloader picks up the new K8s Secret and rolls the backend Deployment. Done automatically.
- [x] 7.5 Backend Pods (`server-app`, `consumer-app`) transition from `ContainerCreating` to `Running`. **Required an additional manual IAM grant**: `backend-app@liverty-music-prod.iam` GSA was missing `roles/cloudsql.client` (same manual binding gap as dev — Pulumi doesn't manage this role; dev has it via a manual gcloud applied historically). Applied via `gcloud projects add-iam-policy-binding`. After grant, `server-app` Pod reached `1/1 Running`. `consumer-app` Pod is scaled to 0 by KEDA (expected — no NATS traffic in greenfield prod). **Follow-up**: a separate change should Pulumi-manage this binding for both dev and prod to eliminate the manual step.
- [x] 7.6 Verify backend → Zitadel auth path is live: `curl -I https://api.liverty-music.app/grpc.health.v1.Health/Check` returns 200 (this exercises the gRPC health endpoint which is auth-exempt). **Verified 200** via `curl -s -X POST -H 'Content-Type: application/json' -d '{}' https://api.liverty-music.app/grpc.health.v1.Health/Check` — Connect-RPC requires POST (the `curl -I` HEAD pattern returns 405 by Connect-RPC design).

## 8. Archive

- [x] 8.1 Update this tasks.md + design.md with any incident notes from the live bootstrap. **Notes captured**: (a) ESO needs manual force-sync after a new GSM Secret appears mid-reconcile (1h refresh interval is too coarse for first-creation reconciliation); (b) `roles/cloudsql.client` is a manual IAM binding for `backend-app` GSA on both dev and prod — separate follow-up needed to Pulumi-manage; (c) Pulumi-up itself completed in ~90s; (d) backend Pod `server-app` reached Running after ~9 min total (Pulumi up + ESO sync + reloader + container start + Pod restart backoff from earlier CrashLoopBackOff state).
- [x] 8.2 Run `openspec validate enable-zitadel-prod-pulumi-provider --strict`. Validated.
- [x] 8.3 Sync delta specs to main specs (`openspec/specs/zitadel-self-hosted-deployment/spec.md` — apply MODIFIED + ADDED operations). Done in archive PR.
- [x] 8.4 Move change directory: `git mv openspec/changes/enable-zitadel-prod-pulumi-provider openspec/changes/archive/2026-05-14-enable-zitadel-prod-pulumi-provider`. Done in archive PR.
- [x] 8.5 Commit + push + merge the archive PR.
- [x] 8.6 Now that backend is up, also archive the `prod-k8s-manifests` change. Bundled into the same archive PR.
