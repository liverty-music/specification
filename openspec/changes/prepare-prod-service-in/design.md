## Context

The `refactor-unify-env-dispatch` change closed the Pulumi-side gap for prod Zitadel/GCP infrastructure, and `consolidate-public-dns-on-cloudflare` (PR #263 in flight) will close the apex DNS + apex TLS cert gap. Even after both land, an end-to-end audit of the prod env-var surface (Pulumi ESC, K8s ConfigMaps, frontend build-time `.env`, GSM secrets, GitHub Actions vars, Artifact Registry IAM) surfaced eight independent gaps that each block real-user service-in. This change bundles them into a single coordinated push because they share sequencing constraints (the cross-project IAM revocation MUST follow successful prod-AR image migration; the frontend prod build MUST consume the prod-`ApplicationOidc` `client_id` produced by Pulumi).

Current state (2026-05-15):
- Prod GKE cluster is `Synced/Healthy` for 13/14 ArgoCD apps; the 14th (`backend-migrations`) reports `Status=Unknown (ComparisonError)` because `liverty-music/backend:k8s/atlas/overlays/prod/` does not exist.
- All prod Pod images pull from `liverty-music-dev/{backend,frontend}` Artifact Registry. Cross-project pull is permitted by a manual, Pulumi-invisible IAM grant on `gke-node@liverty-music-prod` that wasn't part of any IaC.
- `frontend/.env` is single-file with dev URLs (`api.dev.liverty-music.app`, dev OIDC issuer, dev SPA client_id, dev product org id). Vite bakes these into the SPA bundle at build time, so even with apex DNS the prod-served SPA would talk to dev API.
- `liverty-music/prod` ESC has zero seeded values for `gcp.monitoring.slackNotificationChannels.alertBackend`, `gcp.billingAlertEmail`, `gcp.budgetAmountJpy` — so `MonitoringComponent`, `ZitadelMonitoringComponent`, and the billing budget all materialize as dormant no-ops.
- Backend prod ConfigMaps carry placeholder values: `TICKET_SBT_ADDRESS=0x0000…`, `VAPID_PUBLIC_KEY` identical to dev (likely keypair mismatch).
- `liverty-music/prod` ESC carries stale fields (`zitadel.domain`, `zitadel.orgId`) from the pre-self-hosted era; `liverty-music/dev` additionally carries an orphaned `zitadel.pulumiJwtProfileJson`.

## Goals / Non-Goals

**Goals:**

- Make `https://liverty-music.app/` serve the production SPA backed by prod-side APIs, prod identity provider, prod database, and prod blockchain contracts — with no cross-project image dependencies and no dormant alerting/budget gates.
- Establish reusable, declarative patterns for prod-image-pipeline (release-tag-driven), per-env frontend builds (`.env.prod`), and per-env GSM/ESC seeding hygiene that future capabilities can rely on.
- Close the operational debt around the manual `gke-node@prod` IAM grant and the four stale ESC fields, without leaving the system in a half-migrated state at any point.

**Non-Goals:**

- Refactoring the *cadence* of backend Atlas migration authoring (e.g., enforcing prod-only review, blue/green migrations, or automatic rollback). This change only adds the prod *overlay* so ArgoCD stops erroring; migration governance is a separate concern.
- Optimizing prod resource sizing — `prod-k8s-manifests` already mandates "match dev exactly until SLO-driven re-tune"; that re-tune is out of scope here.
- Migrating from ConfigMap-stored `TICKET_SBT_ADDRESS` to GSM-stored (a more rotatable pattern). This change replaces the placeholder with the mainnet value but keeps the ConfigMap location; rotation is a future concern (OQ3).
- Production-grade Atlas rollback procedures.
- Frontend `VITE_PREVIEW_ARTIST_IDS/_NAMES` content tuning — listed as a task because the value differs per env, but the spec-level requirement is operational (curated content), not deployment.
- Removing the `liverty-music-prod` Artifact Registry repos as a separate Pulumi cleanup if cross-project pull is ever reinstated (this change makes the prod-AR canonical, but does not constrain future architectural pivots away from it).

## Decisions

### D1. Release-tag triggers (`release: types: [published]`), not tag-push

GitHub's `release` event fires only when a Release is *published* (not when a tag is pushed). Choosing `release` over alternatives:

| Trigger | Verdict | Why |
|---|---|---|
| `push: tags: [v*]` | ❌ | No binding to GitHub Environment unless every workflow file explicitly names `environment:` — error-prone and forks the dev/prod auth pattern. |
| `workflow_dispatch` | ❌ | Loses the "Release == source of truth" property; operators can run prod builds against any branch. |
| `release: types: [published]` | ✅ | Implicit Environment binding via `environment: prod`; release tag is the immutable input; the GitHub Releases UI gives operators a single button to ship. |

The dev path (`push: branches: [main]`) is preserved unchanged — both events live in the same workflow file, with a job-level conditional selecting AR target + image tag set.

### D2. `.env.prod` over Docker build-args for env separation

Vite supports `--mode prod` natively, loading `.env.prod` (in addition to `.env`) at build time. The prod workflow runs `npm run build -- --mode prod`; the dev workflow runs the existing build. Build-args via Dockerfile would require declaring `ARG VITE_<KEY>` for every key (≈10 in `.env`) and threading them through `RUN`, doubling the surface area for no observable benefit.

### D3. `.env.prod` is committed to the repo, not pulled from ESC

All `VITE_*` values are public by SPA convention (`AuthMethodType=NONE` means the OIDC client_id is unguarded; VAPID public key is, by definition, public; preview artist IDs are non-sensitive). Committing `.env.prod` to `liverty-music/frontend` matches the existing `.env` precedent and avoids introducing a build-time ESC dependency (which would require a service-account token, Docker buildx env-injection, etc.). If a future secret ever needs to land in the SPA, revisit; until then, plain-file commit wins.

### D4. IAM revocation is the LAST step, gated by deploy verification

The manual `gke-node@prod → roles/artifactregistry.reader on liverty-music-dev` grant is the single failure point that, if removed too early, cascades into `ImagePullBackOff` on every prod pod simultaneously. Required ordering:

1. Land the prod build pipeline workflows (no behavioral change until first Release cut).
2. Cut a backend Release tag (`vX.Y.Z`) → first prod-AR backend images appear.
3. Provision prod Zitadel `ApplicationOidc` via Pulumi (gives us the `client_id` + product-org-id needed by `.env.prod`).
4. Commit `frontend/.env.prod` with prod values; cut a frontend Release tag → first prod-AR frontend image.
5. Merge cloud-provisioning overlay PR (kustomize `images:` pinning to prod AR + image patch).
6. Wait for ArgoCD reconcile; verify every prod pod's `image:` field begins with `liverty-music-prod/...`.
7. Run `gcloud projects remove-iam-policy-binding liverty-music-dev --member='serviceAccount:gke-node@liverty-music-prod.iam.gserviceaccount.com' --role='roles/artifactregistry.reader'`.
8. Wait 5 min; verify no pod entered `ImagePullBackOff` (would mean a missed reference).

This sequencing is captured both in the `prod-image-pipeline` spec (revocation runbook scenario) and explicitly in tasks.md.

### D5. Image tagging: `vX.Y.Z` + commit SHA, never `:latest`

Prod images carry two tags:
- `vX.Y.Z` — the human-recognized Release tag, useful for `gcloud artifacts docker images list`.
- `<commit-sha>` — the immutable digest pointer, used by ArgoCD Application image references.

`:latest` is forbidden on prod (per spec). Dev retains its existing `:latest + :sha + :main` triple because dev's ArgoCD Image Updater relies on `:latest`. Mixing models per env is acceptable; prod's release cadence is slow enough that the operator-friendly tag scheme outweighs the drift-from-dev cost.

### D6. Atlas prod overlay lives in `liverty-music/backend`, not in `cloud-provisioning`

`cloud-provisioning/k8s/argocd-apps/prod/backend-migrations.yaml` already points at `liverty-music/backend:k8s/atlas/overlays/prod`. The Atlas overlay's source code IS the migration code (backend's responsibility), not infra plumbing (cloud-provisioning's responsibility). No relocation; we just add the missing directory in backend.

### D7. Cross-repo PR fan-out: one PR per repo, sequenced

| Phase | Repo | PR contents | Reviewer concern |
|---|---|---|---|
| 1 | `specification` | This change's artifacts (proposal, design, specs, tasks) | Spec-level review, requirements completeness |
| 2 | `cloud-provisioning` | Prod `ApplicationOidc` Pulumi resource; prod overlay kustomize `images:` pinning; runbook updates | Pulumi preview review + kustomize render diff |
| 3 | `backend` | `deploy.yml` Release-trigger path; `k8s/atlas/overlays/prod/` | CI workflow review + Atlas overlay sanity |
| 4 | `frontend` | `push-image.yaml` Release-trigger path; `.env.prod` committed | CI workflow + bundle-bake assertion |

PRs 2-4 can run in parallel after PR 1 lands (none depend on each other for code; they depend operationally on the artifact sequence in D4).

### D8. Stale ESC field cleanup via `esc env rm`, not Pulumi

ESC is provisioned separately from Pulumi stack state. Removing the three stale fields (`zitadel.domain`, `zitadel.orgId`, `zitadel.pulumiJwtProfileJson`) is an `esc env rm` operation on `liverty-music/dev` and `liverty-music/prod`, not a Pulumi diff. Pre-flight: `grep -rn <field>` across the cloud-provisioning repo to confirm zero readers. Post-flight: a no-op `pulumi preview` should succeed (proof of no inadvertent reader).

### D9. VAPID keypair: investigate first, regenerate only if mismatched

Mode A (preferred if true): the prod `vapid-private-key` GSM secret was seeded from the **same** keypair as dev. In that case, the configmap public key is correct (matches by definition) and no action is needed — just record the invariant in spec.

Mode B (likely given the audit comment "placeholder; replace with prod public key before launch"): the GSM private key was rotated to a prod-specific value at some point but the configmap public key was forgotten. In that case, generate a new keypair fresh:
- `openssl ecparam -name prime256v1 -genkey -noout -out vapid-private.pem`
- Derive the public point as Base64URL-encoded uncompressed P-256 point.
- `esc env set liverty-music/prod pulumiConfig.gcp.vapidPrivateKey "$(cat vapid-private.pem)" --secret`
- Update `VAPID_PUBLIC_KEY` in three backend prod configmaps + `VITE_VAPID_PUBLIC_KEY` in `frontend/.env.prod`.
- `pulumi up --stack prod` to push the new GSM secret version; rollout via Reloader.

Determination of Mode A vs Mode B is itself a task (decrypt the prod GSM secret, derive public, compare to configmap).

### D10. Mainnet SBT contract deployment: external, but spec-required

The contract deploy itself is outside this change's code scope (it's a smart-contract operation against a public chain). The spec requires the address NOT be the zero address; the task list captures the operator action (deploy contract, record address in three configmap.env files). The verification scenario in the spec is a checksum + on-chain bytecode probe.

## Risks / Trade-offs

[**R1: Frontend release tag cut before prod ApplicationOidc exists**] → Frontend `.env.prod` would have to embed a placeholder client_id, prod sign-in would fail until the configmap is rebuilt. **Mitigation**: Explicit phase ordering in tasks.md (Pulumi prod apply for ApplicationOidc BEFORE frontend Release tag), with a manual verification step that the prod ApplicationOidc client_id is present in `frontend/.env.prod` before tag publish.

[**R2: IAM revocation too early**] → Every prod pod enters `ImagePullBackOff` simultaneously, requiring re-grant + cluster patience. **Mitigation**: D4 sequencing + explicit verification step before revocation; runbook warns prominently.

[**R3: `--mode prod` flag missing in prod workflow**] → Vite silently uses `.env` (dev hostnames) and produces a "prod" build that still talks to dev. **Mitigation**: Spec scenario "no dev hostnames in prod bundle" gives a CI-testable invariant (grep static assets for `dev.liverty-music.app`).

[**R4: Mainnet SBT contract has ABI incompatibility with backend**] → Ticket-minting RPCs fail at runtime even though both halves "look correct". **Mitigation**: Pre-deploy smoke — run the backend's existing `Etherscan`-style integration test against the mainnet contract address before flipping the configmap.

[**R5: `esc env rm` of stale field breaks an undocumented reader**] → Some script or future operator's expectation silently breaks. **Mitigation**: `grep -rn` across all four repos before the `esc env rm` call; `pulumi preview --stack <env>` after, expecting zero diff.

[**R6: Atlas prod migration applies destructively on first run**] → Migration that ran cleanly in dev (e.g., due to dev's existing schema state) tries to drop a prod-only table that pre-exists. **Mitigation**: Operator runs the first prod Atlas apply against a Cloud SQL snapshot first, or manually inspects the migration plan via `atlas migrate diff` against prod before merging the prod-overlay PR. Captured in Atlas overlay task as a manual verification step.

[**R7: Bundle-bake assertion has false negatives**] → A test like "grep static assets for `dev.liverty-music.app`" might pass even if Vite minified the string. **Mitigation**: Combined assertion uses three checks (no `dev.liverty-music.app`, presence of `api.liverty-music.app`, presence of `auth.liverty-music.app`); minification-resistant in practice because URLs survive minification as string literals.

[**R8: Stale ESC field removal silently breaks an old archived change's reproducibility**] → A hypothetical archive replay would fail. **Mitigation**: Accepted — archived changes are historical artifacts, not re-runnable. Documented in the change's archive note when this lands.

## Migration Plan

1. **Phase 1** — Merge specification PR (this change's artifacts).
2. **Phase 2** — Cloud-provisioning PR: add prod `ApplicationOidc` Pulumi resource (`web-frontend` SPA OIDC client in prod `liverty-music` product org); export its `client_id` and the prod product-org-id via Pulumi stack outputs.
3. **Phase 3** — Operator: `pulumi up --stack prod` to provision the prod `ApplicationOidc`. Record client_id + product-org-id from Pulumi outputs.
4. **Phase 4** — Backend PR: extend `deploy.yml` with Release-trigger path; new `k8s/atlas/overlays/prod/` directory.
5. **Phase 5** — Backend Release tag cut (`v1.0.0`): first prod images pushed to `liverty-music-prod/backend`.
6. **Phase 6** — Frontend PR: extend `push-image.yaml` with Release-trigger path; commit `.env.prod` with prod values (using Phase 3's recorded client_id + org_id; apex API URL; apex issuer; prod VAPID public key per D9 outcome; info log level).
7. **Phase 7** — Frontend Release tag cut: first prod image pushed to `liverty-music-prod/frontend/web-app`.
8. **Phase 8** — Cloud-provisioning PR: kustomize prod overlay image-pinning patches; runbook updates for IAM revocation.
9. **Phase 9** — Operator: merge cloud-provisioning PR; wait for ArgoCD prod reconciliation; verify all prod pods running on prod-AR images.
10. **Phase 10** — Operator: `gcloud projects remove-iam-policy-binding liverty-music-dev` (per D4 step 7).
11. **Phase 11** — Operator: `esc env set liverty-music/prod` for `gcp.monitoring.slackNotificationChannels.alertBackend`, `gcp.billingAlertEmail`, `gcp.budgetAmountJpy`.
12. **Phase 12** — Operator: deploy mainnet ticket SBT contract; update three configmap.env files with mainnet address (committed in cloud-provisioning).
13. **Phase 13** — Operator: VAPID keypair verification (D9); if mismatch, regenerate + update configmaps + ESC.
14. **Phase 14** — Operator: `esc env rm` for stale fields (`zitadel.domain`, `zitadel.orgId`, `zitadel.pulumiJwtProfileJson`) in both `liverty-music/dev` and `liverty-music/prod`.
15. **Phase 15** — Operator: `pulumi up --stack prod` final pass to materialize MonitoringComponent + budget; smoke test `https://liverty-music.app/` end-to-end (sign-up, sign-in, follow artist, push notification).

**Rollback strategy**:
- Phases 5/7 — re-cut a prior Release tag; ArgoCD will pin to the older image.
- Phase 10 — re-add the IAM grant via `gcloud projects add-iam-policy-binding`.
- Phase 11 — `esc env rm` of the just-added keys (Pulumi auto-removes the gated resources on next `pulumi up`).
- Phase 14 — `esc env set` to re-add the removed field with its original value (operators MUST capture each field's value before deletion, in a paste-bin or `tmp/` file, for rollback eligibility).

## Open Questions

- **OQ1**: Does the existing `prod` GitHub Environment (set up by Pulumi's `GitHubRepositoryComponent` with reviewers + branch protections) work for Release events the same way it works for push events? If reviewers are required for `push: main → dev` already, do Release-triggered jobs also gate on the same reviewers? Likely yes (Environment protection is event-type-agnostic), but verify before Phase 5.

- **OQ2**: Should `.env.prod` live in `frontend` (committed) or in `cloud-provisioning` (env-managed)? D3 commits in `frontend` for simplicity, but if we ever need to inject build-time secrets (e.g., per-env Sentry DSN with sampling token), the file location decision should be revisited. Current call: defer.

- **OQ3**: Is `TICKET_SBT_ADDRESS` better stored in GSM (rotatable, mainnet-redeploy-tolerant) than in K8s ConfigMap? Mainnet contracts are typically immutable, so the ConfigMap pattern is acceptable. If we ever upgrade the contract architecture (e.g., proxy + impl), revisit. Current call: keep in ConfigMap; document the rotation runbook as a follow-up.

- **OQ4**: Does the first prod Atlas migration apply destroy any pre-existing data? Cloud SQL prod was provisioned fresh on 2026-05-12 with only Zitadel's schema initialized via `ZITADEL_FIRSTINSTANCE`; the `liverty-music` (backend) database has no pre-existing tables. Expectation: zero-risk apply. Operator should still inspect `kubectl describe atlasmigration` output for the first prod apply.
