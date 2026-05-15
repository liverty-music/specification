## Context

The prior change `enable-zitadel-prod-pulumi-provider` (archived 2026-05-14) wired the Zitadel Pulumi provider + the `backend-app` machine user into prod via a single `BackendMachineKeyComponent`. That delivered backend ↔ Zitadel JWT auth (programmatic), but left **9 of the dev `Zitadel` class's 12 Zitadel-side components** unwired for prod. Concretely, today's prod state:

- No browser user (operator or end-user) can sign in. `https://auth.liverty-music.app/ui/console` returns 401 — there's no `login-client` PAT for the `zitadel-web` Pod to authenticate to Zitadel.
- No verification emails go out. There's no `SmtpConfig` + activation against the prod Zitadel instance.
- The frontend SPA on `https://liverty-music.app` has no `ApplicationOidc` client to redirect to.
- Access tokens issued by prod Zitadel lack the `email` claim — the backend's `ValidateIdentity` code path fails closed when `email` is absent.

The dev path proves out the full topology: one `Zitadel` class instantiating Provider + admin org (imported) + product org + Project + Frontend + Smtp + ActionsV2 + MachineUser(backend-app) + LoginClient + GoogleAdminIdp + AdminOrgConfig + HumanAdmin + E2eTestUser, in a strict dependency order. Prod needs the same set minus `E2eTestUserComponent` (E2E test infra is a separate concern, scoped to a follow-up after launch).

The existing dev `Zitadel` class throws on `env !== 'dev'` deliberately — it bakes in the assumption that the instance can be addressed via a single `ZitadelArgs` bundle. Re-using the class for prod would require either (a) loosening the env guard, (b) duplicating it as `ZitadelProd`, or (c) extracting a new top-level component that internally wires the 9 leaf components without touching dev's class. The constraint that the `src/index.ts` dispatch line stays thin (per `CLAUDE.md` "Main entry point dispatching to GCP and GitHub components") and that dev URNs must not churn drives the choice.

Stakeholders:
- **Operator** (`pannpers@pannpers.dev`): needs Console access to the prod instance via Google SSO.
- **End users** (prod fan accounts): need the SPA's OIDC sign-in + sign-up flow to work, including email verification.
- **Backend service**: depends on the `email` claim being present in access tokens (hardened by the cutover-incident chain in dev).
- **Zitadel-web Pod**: currently `ContainerCreating`, blocked waiting on `zitadel-web-pat` K8s Secret (synced from GSM `zitadel-login-pat` by ESO).

## Goals / Non-Goals

**Goals:**

- Reach dev parity for the prod Zitadel application-level stack: end-user OIDC sign-in via SPA, sign-up email verification, operator Console access via Google SSO, access tokens carrying `email`.
- Land all 9 missing components in a single coherent Pulumi unit so the prod cutover is atomic — partial states (e.g., admin LoginPolicy without the Google IdP) would lock operators out mid-cutover.
- Zero URN churn on dev. Dev's `Zitadel` class stays verbatim; existing dev URNs continue to map 1:1 to the same resources.
- Keep the `src/index.ts` prod block as one dispatch line, parallel to dev's `new Zitadel(...)` line.
- Preserve blast-radius separation (per the archived `enable-zitadel-prod-pulumi-provider` D2): `backend-app` lives in product org with ORG_USER_MANAGER, operator identities (pulumi-admin, login-client, IAM_OWNERs) live in admin org.

**Non-Goals:**

- `E2eTestUserComponent` for prod. E2E tests run against dev exclusively today; prod E2E is a follow-up scoped post-launch as `enable-zitadel-prod-e2e-user`.
- Refactoring dev's `Zitadel` class into a shared base. The 13-component dev assembly stays unchanged. The new prod class is a *parallel* assembly, not a refactor of the dev one.
- Cross-repo follow-ups: backend Atlas migration prod overlay, frontend `.env.prod` + CI/CD branch→env mapping. Those are tracked in separate repo PRs.
- Pulumi-managed adoption of operational-debt IAM bindings (`cloudsql.client`, cross-project AR IAM, ESO refresh tuning). Carried forward from the archived `enable-zitadel-prod-pulumi-provider` follow-ups.
- The Cloudflare apex `liverty-music.app` A record (out of scope per `prod-environment-bootstrap` design D2).

## Decisions

### D1 — Extract `ZitadelProdStackComponent` as a top-level wrapper; do NOT mutate dev's `Zitadel` class

**Decision:** Create a new `ZitadelProdStackComponent extends pulumi.ComponentResource` at `src/zitadel/components/zitadel-prod-stack.ts`. It internally instantiates the 9 leaf components in the same dependency order dev's class uses, parallel to how `BackendMachineKeyComponent` today wraps `MachineUserComponent` + the product-org `Org` + the GSM Secret bundle. The prod block in `src/index.ts` becomes a single `new ZitadelProdStackComponent(...)` line, replacing today's `new BackendMachineKeyComponent(...)` line.

**Rationale:**

- **Zero dev URN churn.** Dev's `new Zitadel(...)` line and the 13 child URNs underneath it stay byte-identical. The new prod stack lives in a separate URN namespace (`zitadel:liverty-music:ZitadelProdStack$...`), so dev's preview shows `0 to do` for Zitadel even after this change merges.
- **Thin dispatch line preserved.** `src/index.ts` keeps the "dispatch only" shape per `CLAUDE.md`. Anything else (env-specific ESC pulls, two-org wiring, conditional E2E user) lives inside the component.
- **Atomic blast radius.** Wrapping the 9 components in a `ComponentResource` means a single `pulumi destroy --target` (in some recovery scenario) cleans the entire prod Zitadel stack at once, instead of leaving partial state across 9 leaves. Matches the recovery model in `docs/runbooks/pulumi-state-recovery.md`.
- **Alternative considered (rejected): refactor dev's `Zitadel` class to be env-parameterized.** Cost: every dev resource URN changes (the env guard removal + arg signature change), forcing a Pulumi state migration on dev. Benefit: one class instead of two. Net: not worth it given dev is settled and prod adoption is the constrained path.
- **Alternative considered (rejected): instantiate the 9 leaf components directly from `src/index.ts`'s prod block.** Cost: 9-line block in `index.ts` violates the thin-dispatch principle; future cross-component refactors touch `index.ts` instead of staying scoped. Benefit: no new wrapper class. Net: rejected because the same pattern already exists for backend-app via `BackendMachineKeyComponent`, so adding a second wrapper is the consistent path.

### D2 — Bring the prod `admin` org into Pulumi state via one-time `pulumi import`

**Decision:** The prod `admin` org is auto-created by Zitadel's first-instance bootstrap (driven by `ZITADEL_FIRSTINSTANCE_ORG_NAME=admin` in the configmap, already merged via the `prod-k8s-manifests` change). Before the first `pulumi up --stack prod` of this change, the operator runs once:

```bash
pulumi import zitadel:index/org:Org admin <prod-admin-org-id> --stack prod
```

The org id is fetched via the Zitadel admin API using the bootstrap-uploaded `pulumi-admin` JWT (the `zitadel-machine-key-for-pulumi-admin` GSM secret already exists in prod). Documented as a pre-flight step in tasks.md §1.

**Rationale:**

- **Cannot `new zitadel.Org('admin', ...)` from Pulumi.** Zitadel does not expose a creation API that idempotently adopts an existing org by name; a second `Org` create would either fail or duplicate. The bootstrap-created org has the `IsDefault=true` flag set by Zitadel itself.
- **`protect: true` is mandatory on the resulting resource.** `pulumi destroy` against the imported admin org would lock all operators out — the `pulumi-admin` MachineUser the provider authenticates as lives inside it. Mirrors the dev path (`src/zitadel/index.ts` line 214).
- **Alternative considered (rejected): write a Pulumi dynamic resource that discovers the admin org id via the Zitadel admin API on every preview/up.** Cost: extra API roundtrip every preview, dynamic resource state churn, and the prod admin org id is stable (never re-bootstraps), so a one-time import is the simpler answer. Benefit: no operator-visible pre-flight step. Net: rejected; the dev path uses the same one-time-import shape.

### D3 — Bundle all 9 components in this single change instead of merging them one-by-one

**Decision:** Land Frontend + Smtp + ActionsV2 + LoginClient + GoogleAdminIdp + AdminOrgConfig + HumanAdmin + ProjectComponent + admin-org import in one Pulumi `up`. Do not split into 9 PRs.

**Rationale:**

- **Inter-component dependencies create unsafe intermediate states.** Examples:
  - `AdminOrgConfigComponent` sets `LoginPolicy.userLogin=false`. Without `GoogleAdminIdpComponent` (referenced by the same policy via `idps=[googleIdpId]`), the admin org has no usable sign-in method and the operator is locked out of `/ui/console`.
  - `HumanAdminComponent` provisions `pannpers` and pre-links the Google sub via `ZitadelUserIdpLink`. Without the Google IdP in the admin org's LoginPolicy, the link is referenced but unreachable.
  - `FrontendComponent` creates `ApplicationOidc` + product-org `LoginPolicy`. Without the policy, the SPA's redirect succeeds at the OIDC layer but the Login V2 UI presents an empty sign-in form (no userLogin, no IdPs, no passkey).
- **`pulumi up --stack prod` is a manual operator action.** Bundling means one operator-attended deployment, one preview review, one verification window. Splitting means 9.
- **Alternative considered (rejected): bundle only the inter-dependent quartet (Frontend + Smtp + LoginClient + ActionsV2) and ship the admin org cluster (GoogleIdp + AdminOrgConfig + HumanAdmin) in a follow-up.** Cost: leaves Console operator-locked for a deployment cycle and forces a second `pulumi import` window. Benefit: smaller preview. Net: rejected — the components are tightly coupled.
- **Alternative considered (rejected): land the admin-org-side stack first (so Console works), then end-user-side.** Cost: end-user sign-up emails stay broken between cuts, observable as silent failures in prod sign-up. Benefit: operator can debug from Console mid-cutover. Net: marginal benefit, rejected.

### D4 — Wrap `getSecretVersionAccessOutput` results and `MachineKey.keyDetails` in `pulumi.secret()` consistently across all 9 components

**Decision:** Every code path inside `ZitadelProdStackComponent` that reads `zitadel-machine-key-for-pulumi-admin` from GSM (for the Provider's `jwtProfileJson`, for the `SmtpActivation` dynamic-resource Zitadel admin-API call, for `HumanAdminComponent`'s dynamic admin-API call) MUST wrap the result in `pulumi.secret()`. Same rule for the `MachineKey.keyDetails` output emitted by `LoginClientComponent` (the new login-client PAT) and any other Zitadel `Output<string>` carrying credential bytes.

**Rationale:**

- **`@pulumi/gcp`'s `getSecretVersionAccessOutput` does NOT mark its output secret.** The dev path's `src/zitadel/index.ts:170` and `BackendMachineKeyComponent`'s round-2 review fix both prove this: without an explicit `pulumi.secret()` wrap, the RSA private key embedded in the JWT-profile JSON surfaces in `pulumi preview` output (including Pulumi Cloud PR previews), CI logs, and Pulumi service state history.
- **`@pulumiverse/zitadel`'s `MachineKey.keyDetails` is a plain `Output<string>`.** Same leak risk for any newly-issued JWT-profile keys (none expected from this change's 9 components beyond `loginClientToken` for the PAT, but the rule applies uniformly).
- Same protection pattern as `BackendMachineKeyComponent` (`src/zitadel/components/backend-machine-key.ts:109-116, 170`).

### D5 — Defer `E2eTestUserComponent` to a separate follow-up change

**Decision:** Do not provision the prod E2E test user in this change. Track as a follow-up `enable-zitadel-prod-e2e-user`.

**Rationale:**

- **E2E test infra is operationally distinct.** The dev E2E user requires Playwright credentials in ESC (`pulumiConfig.zitadel.e2eTestUser.password`), a CI/CD job to capture session state from `auth.dev.liverty-music.app`, and the `.auth/` directory convention (per memory `reference_e2e_auth.md`). Prod E2E adds: separate test-tenant decision (do we test against real prod data or a side namespace?), GitOps wiring for the prod `.auth/` capture job, and prod-data-leakage risk review.
- **None of the 9 components in this change depend on it.** Removing E2E from scope shrinks the preview, reduces ESC seeding (no `e2eTestUser.password` needed), and avoids tying the operator-unblock and end-user-unblock outcomes to a test-infra decision.
- **Alternative considered (rejected): include with a feature flag.** Cost: dead code in prod state until activated. Benefit: pre-provision the GSM Secret shell. Net: rejected — adds complexity without unblocking anything.

### D6 — Admin org keeps `isDefault: true`; product org `isDefault: false`

**Decision:** When the prod admin org is imported, its `IsDefault=true` flag (set by the bootstrap) is preserved in Pulumi state. The new product org is created with `isDefault: false`. Mirrors dev exactly.

**Rationale:**

- **Console routing depends on the default org's `LoginPolicy`.** Empirically verified in dev (per `src/zitadel/index.ts:193-207` comment): Zitadel's Console OIDC AuthN does not include an `org_id`, so Login V2 uses the **default org's own LoginPolicy**. If the product org were default, Console would hit the passkey + register policy and the Google sign-in button would never appear. Making `admin` the default routes Console to the Google-IdP path.
- **End-user OIDC traffic from the SPA is unaffected** because the `ApplicationOidc` client owned by the `liverty-music` Project (product org) carries that org's id in its AuthN context. Zitadel resolves the client_id to the product org regardless of the default flag.

### D7 — Out-of-band: Google Cloud Console OAuth 2.0 Web Application client for prod

**Decision:** Before the first `pulumi up --stack prod` of this change, the operator manually creates a Google Cloud Console OAuth 2.0 Web Application client for prod (separate from the dev client). Authorized redirect URI: `https://auth.liverty-music.app/ui/v2/login/login/callback`. The resulting `client_id` and `client_secret` are seeded into `liverty-music/prod` ESC via `esc env set pulumiConfig.zitadel.googleAdminIdp.clientId ...` (and `.clientSecret ... --secret`).

**Rationale:**

- **Google OAuth clients are not Pulumi-managed.** No Google API supports IaC creation of OAuth clients on a Google Cloud project — the Cloud Console GUI is the only path. Same constraint applied to dev (the dev Google client exists out-of-band).
- **Why a separate client (not reuse dev's):** distinct authorized redirect URIs (dev's `auth.dev.liverty-music.app` vs. prod's `auth.liverty-music.app`) and credential separation (a dev client_secret leak shouldn't compromise prod operator sign-in).

### D8 — Use the `api-client.ts` dynamic resource (not a Pulumi-managed `zitadel.*` resource) for the human admin's IdP link

**Decision:** `HumanAdminComponent` provisions `pannpers@pannpers.dev` as a `zitadel.HumanUser` (Pulumi-managed) + grants `IAM_OWNER` via an instance-level `OrgMember`, then uses the existing `dynamic/user-idp-link.ts` dynamic resource (backed by `dynamic/api-client.ts`) to link the local user to the prod Google IdP.

**Rationale:**

- **`@pulumiverse/zitadel` does not expose user→IdP link as a managed resource.** The dev path uses the same dynamic resource. Re-using it for prod is a straight reuse — no new code paths.
- **Why pre-link instead of relying on first-sign-in auto-link:** the admin org's LoginPolicy disables auto-create (`allowRegister=false`) and userLogin (`userLogin=false`). Without a pre-existing link, the operator's first Console sign-in resolves to "no matching local user" and Login V2 returns an error. Pre-linking via the dynamic resource guarantees the first `/ui/console` sign-in succeeds.
- The dynamic resource consumes the admin JWT (`zitadel-machine-key-for-pulumi-admin`) to call the Zitadel Management API. The JWT is read from GSM via `getSecretVersionAccessOutput` and wrapped in `pulumi.secret()` per D4.

### D9 — Store the `login-client` PAT in GSM as `zitadel-login-pat`; ESO mirrors to K8s; Reloader rolls `zitadel-web`

**Decision:** `LoginClientComponent` creates the `login-client` MachineUser + instance-level `IAM_LOGIN_CLIENT` role + `PersonalAccessToken`. The component writes the PAT to a new GSM Secret `zitadel-login-pat` (Pulumi-created + version + IAM binding for the ESO Workload Identity SA). The existing K8s overlay for `zitadel-web` already references `zitadel-web-pat` via ExternalSecret; ESO maps GSM `zitadel-login-pat` → K8s `zitadel-web-pat` Secret, and Reloader rolls the Deployment.

**Rationale:**

- **`zitadel-web` Pod is currently `ContainerCreating`, blocked on the missing K8s Secret.** Naming the GSM Secret `zitadel-login-pat` matches the convention used in `prod-k8s-manifests` ExternalSecret CRs (per archived spec). The same pattern as the dev path (`src/zitadel/index.ts` lines 279-284 plus the dev k8s overlay).
- **Why GSM (not direct K8s Secret):** the dev path uses GSM + ESO; deviating in prod would create a divergent ops contract. GSM also provides audit logging of PAT access via Cloud Logging.

## Risks / Trade-offs

| Risk | Mitigation |
|---|---|
| **Admin-org `pulumi import` fails** (wrong org id, bootstrap not yet run, JWT not in GSM) → first `pulumi up --stack prod` of this change can't proceed | tasks.md §1 explicitly fetches the org id via `curl` against the Zitadel admin API as a pre-flight step; documented prerequisite. |
| **Out-of-band Google OAuth client not created** before `pulumi up --stack prod` → `GoogleAdminIdpComponent` create fails on bad credentials | tasks.md §2 lists the Google Cloud Console URL + redirect URI to create the client before the deploy. ESC seeding for `googleAdminIdp.clientId/clientSecret` is also pre-flight. |
| **Postmark SMTP activation fails** (dynamic resource calls the Zitadel admin API's `_activate` endpoint) → sign-up emails still don't go out | Same dev path is proven; the dynamic resource `dynamic/smtp-activation.ts` retries on transient failures. Verification step in tasks.md §10 sends a smoke email to the operator inbox. |
| **`ZitadelUserIdpLink` (dynamic resource) failure on first deploy** leaves `pannpers` un-linked → operator can't sign in to Console | tasks.md §10 smoke-tests Console sign-in immediately after `pulumi up`. If link failed, re-run the dynamic resource (idempotent) via `pulumi up --target zitadel:liverty-music:ZitadelProdStack$...$pannpers-idp-link`. |
| **Admin LoginPolicy ordering hazard:** if `AdminOrgConfigComponent` applies *before* `GoogleAdminIdpComponent`, the policy references a non-existent IdP id and Pulumi-graph cycle creates rollback complexity | The component's `dependsOn: [googleAdminIdp.idp]` explicit dependency forces ordering. Mirrors dev's wiring exactly. |
| **`SmtpConfig` activation pre-empts an instance-level default config** → existing dev SMTP configuration would be unaffected, but if prod was pre-seeded out-of-band with a different SMTP config, the dynamic activation could conflict | `tasks.md §1` pre-flight checks the Zitadel admin API for existing SMTP configs and documents a manual cleanup step if any are present. |
| **ESC seeding leak risk:** copy-paste of `clientSecret` or `pulumiJwtProfileJson` outside `esc env set --secret` would persist in shell history | tasks.md §2 explicitly uses `--secret` flag on every secret-marked value and instructs the operator to source values from a secure password manager, not shell history. |
| **`pulumi up --stack prod` is manual** (per `CLAUDE.md` "Pulumi Deployments (Automated)") → no auto-deploy on PR merge → window between PR merge and deployment leaves prod docs/state out-of-sync | Explicit step in tasks.md to manually trigger from Pulumi Cloud console. Verified state in archive step. |

## Migration Plan

**Phase 1 — Pre-flight (out-of-band):**

1. Create the prod Google OAuth 2.0 Web Application client in Google Cloud Console. Authorized redirect URI: `https://auth.liverty-music.app/ui/v2/login/login/callback`.
2. Seed ESC `liverty-music/prod`:
   - `pulumiConfig.zitadel.googleAdminIdp.clientId` (plaintext)
   - `pulumiConfig.zitadel.googleAdminIdp.clientSecret` (secret-marked)
   - `pulumiConfig.zitadel.adminGoogleSubs.pannpers` (same `sub` claim as dev — pannpers@pannpers.dev; secret-marked for consistency)
   - `pulumiConfig.zitadel.pulumiJwtProfileJson` (admin JWT for HumanAdminComponent's dynamic resource; secret-marked)
3. Fetch the prod admin-org-id via the Zitadel admin API using the bootstrap-uploaded `pulumi-admin` JWT. Verify the bootstrap-uploader sidecar has completed by checking the `zitadel-machine-key-for-pulumi-admin` GSM Secret has a non-empty `latest` version.

**Phase 2 — Pulumi import (one-time):**

```bash
pulumi import zitadel:index/org:Org admin <prod-admin-org-id> --stack prod
```

Verify the import added the resource to state without churn; commit the resulting `Pulumi.prod.yaml` if any pinned URN refs were emitted.

**Phase 3 — Deploy:**

1. PR merges to `main` after CI passes (PR triggers `pulumi preview` only on prod; verify preview matches expected ~25 new resources).
2. Operator manually triggers `pulumi up --stack prod` from Pulumi Cloud console: https://app.pulumi.com/pannpers/liverty-music/prod/deployments
3. Watch the deploy logs for any of the 5 known-risk components (admin LoginPolicy, SMTP activation, IdP link, login-client PAT, frontend ApplicationOidc).

**Phase 4 — Verification (per tasks.md §10):**

1. SPA sign-in flow: visit `https://liverty-music.app`, complete OIDC redirect, verify the prod Login V2 UI presents passkey + username/password, complete a test sign-up, verify the verification email arrives via Postmark.
2. Operator Console sign-in: visit `https://auth.liverty-music.app/ui/console`, click "Sign in with Google", complete OAuth, verify resolution to `pannpers@pannpers.dev` with IAM_OWNER role.
3. Backend smoke test: capture a token from the SPA flow, decode JWT claims, verify `email` claim is present (proves ActionsV2 webhook is wired and firing on the prod `preaccesstoken` flow).
4. ESO refresh: `kubectl get externalsecret -n zitadel zitadel-web-secrets -o yaml` — verify `Status=Ready` and the synced K8s Secret `zitadel-web-pat` has a non-empty token.
5. Reloader rolls `zitadel-web` Deployment; Pod transitions from `ContainerCreating` to `Running` (1/1 Ready).

**Rollback Strategy:**

- **Partial deploy failure (e.g., SMTP activation fails):** Pulumi's normal rollback semantics apply for the failing leaf; other leaves stay provisioned. Re-run `pulumi up` after fixing the underlying cause (most failures are upstream transient — Zitadel API rate limit, GSM secret access race).
- **Total rollback (extreme):** `pulumi destroy --target <ZitadelProdStackComponent URN> --stack prod` from a fresh `pulumi up` baseline. Per `docs/runbooks/pulumi-state-recovery.md`, the `--target` flag scopes destroy to the component subtree. The admin org's `protect: true` flag survives any partial destroy, preventing operator lock-out.
- **Admin LoginPolicy lockout (operator cannot sign in to Console):** the `pulumi-admin` MachineUser path always works (bypasses LoginPolicy); operator can re-run `pulumi up` to restore the policy from state.

## Open Questions

- **OQ1: Should the `loginClientToken` be issued with an expiry?** Dev currently issues it without expiration (per `LoginClientComponent`). Prod could mirror, but a 90d rotation cycle (with the GSM SecretVersion rotation pattern) would limit blast radius if the K8s Secret leaks. **Provisional answer:** mirror dev (no expiry) for this change; track rotation as an operational-debt follow-up after the prod stack is verified end-to-end. The rotation tooling would apply to dev simultaneously.

- **OQ2: Does prod need a different `humanAdmin` set than dev?** Dev has only `pannpers@pannpers.dev`. Prod could add a second IAM_OWNER (e.g., a co-founder or oncall delegate) for break-glass redundancy. **Provisional answer:** ship with `pannpers` only — matches dev parity and avoids scope creep. Adding a second admin is a one-line component change in a follow-up.

- **OQ3: Should `SmtpComponent`'s `from` address differ between dev and prod?** Dev uses a `noreply@dev.liverty-music.app` convention. Prod's natural default is `noreply@liverty-music.app`. **Provisional answer:** the `SmtpComponent` already env-routes the from address via the `domain` argument it receives; prod will inherit `auth.liverty-music.app` → `noreply@liverty-music.app` automatically, no override needed.

- **OQ4: Will the Cloudflare apex `liverty-music.app` A record be in place before this change deploys?** SPA sign-up flow verification (Phase 4 §1) requires the apex domain to resolve to the prod Gateway. **Provisional answer:** this is a separate concern tracked under `prod-environment-bootstrap` design D2 (Cloudflare DNS out-of-band). Verification in Phase 4 §1 will fail if the A record isn't live, but that's a documentation/comms issue with no scope inside this change.
