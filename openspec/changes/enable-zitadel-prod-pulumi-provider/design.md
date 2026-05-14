## Context

After the `prod-k8s-manifests` change deploy on 2026-05-14, the prod self-hosted Zitadel is running at `https://auth.liverty-music.app` (zitadel-api Pod 3/3 Ready, zitadel-web Pod 1/1 Ready, public OIDC issuer responding). The first-boot bootstrap-uploader sidecar populated `zitadel-machine-key-for-pulumi-admin` GSM Secret with version 1 at 11:12:47 UTC — this is the JWT-profile for the org-admin machine user that Zitadel auto-created during `start-from-init`.

What didn't happen: the planned "second `pulumi up --stack prod`" did not create the backend MachineKey, because the Pulumi code that creates it (`MachineUserComponent`) is invoked only from inside the `Zitadel` class at [`src/zitadel/index.ts`](https://github.com/liverty-music/cloud-provisioning/blob/main/src/zitadel/index.ts), and that class is instantiated only when `env === 'dev'` at [`src/index.ts:74`](https://github.com/liverty-music/cloud-provisioning/blob/main/src/index.ts#L74). The original gate was correct for the SaaS Cloud-tenant Zitadel; it was not lifted when prod switched to self-hosted.

The blast-radius separation that `prod-k8s-manifests` round-12 fix established (org-admin JWT → Pulumi only; backend uses a derived lower-privilege MachineKey) is correct — the gap is purely on the Pulumi side. Five Pulumi resources need to exist after this change runs successfully: the prod Zitadel `MachineUser` and `MachineKey` (Zitadel-provider resources targeting `auth.liverty-music.app`), the GSM `Secret` named `zitadel-machine-key-for-backend-app`, its `SecretVersion`, and the `SecretIamMember` granting ESO read access (all three GCP resources in project `liverty-music-prod`).

Backend Pods on prod are currently stuck in `ContainerCreating` waiting for that GSM Secret. The blocker chain is: this change merges → `pulumi up --stack prod` creates the 5 new resources → ESO syncs the new GSM Secret into the backend namespace → Reloader rolls the backend Deployment → backend Pods reach Running → backend → Zitadel auth path is live.

## Goals / Non-Goals

**Goals:**

- Make `pulumi up --stack prod` create exactly the resources needed for the backend ↔ Zitadel auth path: prod Zitadel `MachineUser`, `MachineKey`, GSM `Secret` + `SecretVersion`, ESO accessor IAM binding.
- Keep the blast-radius separation: the org-admin JWT (`zitadel-machine-key-for-pulumi-admin`) is consumed only by Pulumi at plan/apply time; the GSM SecretVersion that backend mounts is a *separate* JWT for a lower-privilege machine user with the `ORG_USER_MANAGER` role.
- Reuse the dev pattern (`MachineUserComponent`) verbatim — same component, same role assignment, same JWT lifecycle. Differences should be configuration-only (provider URL, org ID, GCP project).
- Land this change before any new feature work that depends on backend → Zitadel auth (currently blocked: backend Pods stuck in `ContainerCreating`).

**Non-Goals:**

- Wiring up the SaaS Zitadel feature set for prod: admin Google IDP (`googleAdminIdpClientId/Secret` ESC values), SMTP (Postmark), ActionsV2 webhooks, productOrg branding, e2e-test-user provisioning. These come when prod actually needs them — they are separate downstream changes.
- Rotating the org-admin JWT (`zitadel-machine-key-for-pulumi-admin`). That key was minted by first-boot bootstrap, and the design intent is "effectively never expires" for the admin tier; rotation is a separate runbook.
- Backfilling Pulumi-managed cross-project Artifact Registry IAM (manual `gcloud projects add-iam-policy-binding` was applied during the `prod-k8s-manifests` deploy — that gets adopted into Pulumi state in a *separate* change).
- Wiring the backend-migrations Application's cross-repo dependency on the backend repo's `k8s/atlas/overlays/prod` (separate backend-repo PR).

## Decisions

### D1: Extract `BackendMachineKeyComponent` (Option B) over lifting the full `Zitadel` class gate (Option A)

**Decision:** Extract a focused, top-level `BackendMachineKeyComponent` that takes minimal inputs (Zitadel provider, org ID, GSM project) and produces the five resources needed (`MachineUser`, `MachineKey`, GSM `Secret`, GSM `SecretVersion`, `SecretIamMember`). Do NOT lift the env gate on the existing `Zitadel` class.

**Why:**

- The existing `Zitadel` class also creates `adminOrg`, `productOrg`, `frontend`, `smtp`, `actionsV2` resources that are NOT needed for prod and would either fail (Zitadel API rejects "admin" org create because it already exists from first-boot bootstrap) or create unwanted side effects (a second `productOrg` distinct from the first-boot org). Adding env conditionals throughout the `Zitadel` class would scatter the dev/prod split across multiple files.
- The minimum component for prod is `Zitadel Provider + MachineUserComponent + GSM Secret + GSM SecretVersion + IAM binding`. Pulling that into a focused top-level component (parallel to `SecretsComponent`) keeps `src/index.ts` readable and makes the prod call site one expressive `new BackendMachineKeyComponent(...)` line.
- `MachineUserComponent` already exists and is stable on dev. The refactor pulls it into the new top-level component as-is; dev's `Zitadel` class becomes the *caller* in dev, prod calls the new component directly. Zero risk to dev's existing behavior.

**Alternative considered (Option A):** Lift the `env === 'dev'` gate on `new Zitadel(...)` and pass `env`-conditional skip flags into the class to disable `adminOrg`/`productOrg`/etc. for prod. Rejected — it broadens an already-complex class, and the prod path would still call the `Zitadel` class with most arguments set to `undefined`, which is confusing at the call site.

### D2: Look up the "admin" org rather than create it

**Decision:** The `BackendMachineKeyComponent` accepts the org ID as a *data input* (resolved via `zitadel.getOrg({ name: 'admin' }, { provider })`) — it does not create the org. The org was auto-created by first-boot via `ZITADEL_FIRSTINSTANCE_ORG_NAME=admin`; trying to `new zitadel.Org(...)` would conflict (the org already exists outside Pulumi state).

**Why:** Aligns Pulumi state with the runtime reality. The first-boot org is owned by Zitadel itself; importing it as a Pulumi-managed resource would tightly couple Zitadel's bootstrap to Pulumi's state and create a destroy-cascade hazard (`pulumi destroy` on prod would attempt to delete the admin org, which is the same org the admin JWT belongs to — circular dependency).

**Alternative considered:** `zitadel.Org` resource with `aliases:` pointing at an imported state. Rejected — the imported state has no Pulumi history, and the lifecycle (Zitadel-managed `firstInstance` vs Pulumi-managed) doesn't fit the alias-rename pattern.

### D3: Provider configuration sources the admin JWT from GSM by URN reference, not by passing the secret value

**Decision:** Configure the Zitadel provider with:

```typescript
const adminJwt = gcp.secretmanager.getSecretVersion({
  project: 'liverty-music-prod',
  secret: 'zitadel-machine-key-for-pulumi-admin',
}, { provider: gcpProvider })

const zitadelProvider = new zitadel.Provider('zitadel-prod', {
  domain: 'auth.liverty-music.app',
  insecure: false,
  jwtProfileJson: adminJwt.then(v => v.secretData),
})
```

The `jwtProfileJson` is a Pulumi `Output<string>` derived from a `getSecretVersion` data source, so it's never serialized to the Pulumi state for the secret itself (just the URN reference + checksum).

**Why:** Avoids round-tripping the JWT through Pulumi config / ESC. The JWT was minted by first-boot bootstrap; the source of truth is GSM. Reading it via a `getSecretVersion` data source on each `pulumi up` ensures Pulumi always uses the current version.

**Risk:** The admin JWT must exist before this code path runs (it does, after the `prod-k8s-manifests` bootstrap-uploader sidecar populates it on first boot — confirmed populated at 11:12:47 UTC 2026-05-14). If somehow the GSM Secret is deleted or the version is disabled, `pulumi up` will fail at preview time with a clear "secret not found" error rather than create a broken MachineUser.

### D4: Effective forever expiration on the prod backend MachineKey

**Decision:** Match dev's pattern verbatim — `expirationDate: '2099-01-01T00:00:00Z'`. The same rotation-runbook gap (no automated rotation today) exists for prod, and a short expiration would cause silent breakage. Comment in code references the dev rationale.

**Why:** This is a known trade-off documented in `zitadel-self-hosted-deployment` spec. Adding rotation is a separate change. Until then, the long-expiration matches dev's stability profile; the alternative (e.g., 90-day expiration) would create operational risk in prod without an existing rotation mechanism.

**Follow-up:** A `zitadel-machine-key-rotation` change introduces a Pulumi-managed rotation cadence + alerting on near-expiry; out of scope here.

## Risks / Trade-offs

- **[Risk] Pulumi `getOrg({ name: 'admin' })` returns a different org than expected** (e.g., if multiple orgs named "admin" exist or if Zitadel's name lookup is loose). → Mitigation: assert on the resolved org's `id` matches what the `zitadel-machine-key-for-pulumi-admin` JWT's `iss` claim expects. Add a runtime check in the component constructor that throws if the lookup returns >1 result or no result.

- **[Risk] First `pulumi up --stack prod` after this change fails because the Zitadel provider can't reach `auth.liverty-music.app`** (e.g., DNS not yet propagating, certificate not yet active). → Mitigation: the prod-k8s-manifests deploy has already verified `auth.liverty-music.app/.well-known/openid-configuration` is live and trusted (the gateway+cert-map is healthy, confirmed via §10 of that change). If it's not, the failure is clear (HTTP error from Zitadel provider) and recoverable via a re-run after DNS/cert is fixed.

- **[Risk] Backend Pod doesn't pick up the new GSM Secret because Reloader doesn't watch GSM directly** (ESO writes a K8s Secret, Reloader watches K8s Secrets — but the backend Deployment may not have the right Reloader annotation). → Mitigation: the backend base manifest already has `reloader.stakater.com/auto: "true"` (confirmed in `prod-k8s-manifests` round-12 D4 design). ESO → K8s Secret → Reloader → Deployment rollout chain has worked on dev for months.

- **[Risk] After this change merges, `pulumi up --stack dev` introduces churn** (because the refactor moves `MachineUserComponent` out of the `Zitadel` class to a new top-level component). → Mitigation: use `aliases: [{ name: 'old-urn' }]` on the new component's `MachineKey` resource to inherit the existing URN, preventing create-replace-delete cycle on the dev MachineKey (which would mint a new key and break dev backend's authn until ESO re-syncs). Memory `reference_pulumi_aliases_urn_rename.md` is the canonical pattern.

- **[Trade-off] No SaaS feature parity in prod for now.** Admin login via Google IDP, SMTP via Postmark, ActionsV2 webhooks — none of these work on prod yet. They are not blockers for the API server: backend ↔ Zitadel auth works via JWT-profile, end-users can self-register via Zitadel's default email/password flow without SMTP (Zitadel logs the verification link instead of emailing it — usable for staged prod testing). Productionizing the admin IDP + SMTP is a separate follow-up.

- **[Trade-off] Effective forever MachineKey expiration carries operational risk.** A leaked JWT-profile cannot be expired without a rotation runbook. → Tracked as the future `zitadel-machine-key-rotation` change. Dev has lived with this trade-off; prod adopts the same posture.

## Migration Plan

1. **Pre-merge prep**:
   - Confirm `auth.liverty-music.app/.well-known/openid-configuration` returns 200 with the Zitadel issuer payload (already verified during `prod-k8s-manifests` §10).
   - Confirm `zitadel-machine-key-for-pulumi-admin` GSM Secret has ≥1 enabled version (already verified — version 1 since 11:12:47 UTC 2026-05-14).
2. **PR + CI**:
   - `pulumi preview --stack dev` shows the refactor's URN moves with `aliases:` set correctly — expect zero replacement (no resource recreation), only a metadata move in state.
   - `pulumi preview --stack prod` shows ~5 resources to create: 1 `MachineUser`, 1 `MachineKey`, 1 GSM `Secret`, 1 `SecretVersion`, 1 IAM `SecretIamMember`. Plus 1 `Output` (parent ComponentResource).
3. **Merge**:
   - Merge triggers auto-deploy on dev (the URN move should be a no-op state-wise; backend behavior unchanged).
   - Prod stays on manual trigger.
4. **Pulumi up for prod (manual, post-merge)**:
   - Trigger `pulumi up --stack prod` from Pulumi Cloud console.
   - Pulumi authenticates to `https://auth.liverty-music.app` using the admin JWT from GSM.
   - Creates the prod `MachineUser` + `MachineKey` in Zitadel.
   - Writes the resulting JWT-profile JSON to GSM SecretVersion `zitadel-machine-key-for-backend-app`.
   - Creates the IAM binding granting ESO read access.
5. **Verification (post-Pulumi-up)**:
   - `gcloud secrets versions list zitadel-machine-key-for-backend-app --project liverty-music-prod` returns ≥1 enabled version.
   - ESO reconciles `zitadel-machine-key-for-backend-app` ExternalSecret in the backend namespace within ~30s.
   - Reloader detects the new K8s Secret and rolls the backend Deployment.
   - Backend Pods (`server-app`, `consumer-app`) transition from `ContainerCreating` to `Running` (~2-3 min total from `pulumi up` completion).
   - `curl -I https://api.liverty-music.app/grpc.health.v1.Health/Check` returns 200.

**Rollback strategy:** If the prod `pulumi up` fails partway:
- Delete any partial resources via `pulumi destroy --target` on the specific URN.
- Re-run after fixing the root cause.
- The backend Pods staying in `ContainerCreating` is the same pre-state as before this change — no regression risk.

## Open Questions

- **OQ1:** Should the prod backend MachineKey live in the "admin" org (first-boot single-org), or should this change also create a separate `productOrg` for prod (matching dev's two-org structure)?
  - *Default decision unless raised:* use the single "admin" org. Two-org separation buys nothing while there are no other product machine users; can be revisited when we have a real reason (e.g., distinct billing or audit boundary).

- **OQ2:** Does the Zitadel `getOrg(name)` data source exist in the `@pulumiverse/zitadel` provider, or do we need to use a different lookup mechanism?
  - *To verify during implementation:* check `@pulumiverse/zitadel` docs / source. If `getOrg` by name doesn't exist, use `getOrgs` + filter, or pass the org ID via ESC (least desirable — couples to a Zitadel-internal ID).

- **OQ3:** Should we surface the new GSM Secret's resource name into the prod backend overlay's `ExternalSecret` *here*, or rely on the dev manifest pattern (which already references `zitadel-machine-key-for-backend-app` by name)?
  - *Default decision unless raised:* the dev pattern is already the canonical reference (per `zitadel-self-hosted-deployment` spec line 164); prod's backend overlay inherits it via the base. No k8s changes needed in this PR — purely Pulumi side.
