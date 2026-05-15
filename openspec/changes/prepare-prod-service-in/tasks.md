## 1. Cloud-provisioning: Prod Zitadel SPA OIDC client (Phase 2 — `liverty-music/cloud-provisioning`)

- [ ] 1.1 Inspect existing `Zitadel` component to confirm the `web-frontend` `ApplicationOidc` is provisioned for all envs (dev already wired); if it's gated on `env === 'dev'`, remove the gate so prod also gets one.
- [ ] 1.2 Export `webFrontendClientId` and `productOrgId` as Pulumi stack outputs so operators can `pulumi stack output` them for `.env.prod`.
- [ ] 1.3 `pulumi preview --stack prod` and capture the diff in the PR description.
- [ ] 1.4 Open PR; review; merge.

## 2. Cloud-provisioning: Prod `ApplicationOidc` apply (Phase 3 — operator-attended)

- [ ] 2.1 Trigger `pulumi up --stack prod` manually via Pulumi Cloud console.
- [ ] 2.2 Verify the new resource appeared in prod stack state.
- [ ] 2.3 Capture `pulumi stack output webFrontendClientId` and `pulumi stack output productOrgId` from the prod stack; paste them into a private notes file under `tmp/` for use in §6.

## 3. Backend: Release-tag-triggered prod build path (Phase 4 — `liverty-music/backend`)

- [ ] 3.1 In `.github/workflows/deploy.yml`, change the trigger block to dual `push: branches: [main]` + `release: types: [published]`.
- [ ] 3.2 Add job-level `environment:` selector: `${{ github.event_name == 'release' && 'prod' || 'dev' }}`.
- [ ] 3.3 In the matrix step "Set Image URI", make `PROJECT_ID` resolve from the selected environment (`vars.PROJECT_ID` already points at `liverty-music-prod` in the prod environment, per existing Pulumi-managed GitHub vars).
- [ ] 3.4 In "Build and Push Docker Image" step, set tags conditionally: dev builds get `${IMAGE_URI}:latest,${IMAGE_URI}:${sha},${IMAGE_URI}:main`; release builds get `${IMAGE_URI}:${github.event.release.tag_name},${IMAGE_URI}:${sha}`.
- [ ] 3.5 Add a job-level guard: prod path SHALL NOT fire on `push` events; dev path SHALL NOT fire on `release` events.
- [ ] 3.6 Verify `make check` (or equivalent) still passes on the workflow YAML.

## 4. Backend: Atlas prod overlay (Phase 4 continued — `liverty-music/backend`)

- [ ] 4.1 Create `liverty-music/backend:k8s/atlas/overlays/prod/kustomization.yaml` mirroring the dev overlay structure.
- [ ] 4.2 Patch the `AtlasMigration` resource for the prod Cloud SQL connection (PSC DNS `298474959c18.25pf3r4b6sfkn.asia-northeast2.sql.goog`, database `liverty-music`, user `backend-app@liverty-music-prod.iam`).
- [ ] 4.3 Confirm the migration source ConfigMap is generated from the same `migrations/` directory as dev (no fork).
- [ ] 4.4 Run `kubectl kustomize k8s/atlas/overlays/prod` locally; verify exit 0 + sensible YAML output.
- [ ] 4.5 Compare the prod overlay's migration plan against the current prod Cloud SQL state via `atlas migrate diff` (dry-run, against prod via an operator's authenticated psql session). Confirm no destructive operations on first apply.
- [ ] 4.6 Open backend PR bundling §3 + §4; review; merge.

## 5. Backend: Cut prod Release (Phase 5 — operator-attended)

- [ ] 5.1 Tag `liverty-music/backend:main` HEAD as `v1.0.0` (or the next semver).
- [ ] 5.2 Publish the GitHub Release for that tag.
- [ ] 5.3 Watch `gh run watch` for `deploy.yml`; confirm all four images (`server`, `consumer`, `concert-discovery`, `artist-image-sync`) pushed to `liverty-music-prod/backend/`.
- [ ] 5.4 Verify via `gcloud artifacts docker images list asia-northeast2-docker.pkg.dev/liverty-music-prod/backend --include-tags` that each image carries both the `v1.0.0` tag and the commit SHA.

## 6. Frontend: `.env.prod` + Release-tag-triggered prod build path (Phase 6 — `liverty-music/frontend`)

- [ ] 6.1 Create `liverty-music/frontend:.env.prod` with the full `VITE_*` key set:
  - `VITE_LOG_LEVEL=info`
  - `VITE_API_BASE_URL=https://api.liverty-music.app`
  - `VITE_ZITADEL_ISSUER=https://auth.liverty-music.app`
  - `VITE_ZITADEL_CLIENT_ID=<webFrontendClientId from §2.3>`
  - `VITE_ZITADEL_ORG_ID=<productOrgId from §2.3>`
  - `VITE_VAPID_PUBLIC_KEY=<from §13>` (placeholder until §13 confirms; commit a temporary value matching dev, then update before tagging)
  - `VITE_PREVIEW_ARTIST_IDS` / `_NAMES` — initial copy from dev; flag follow-up as task §16
- [ ] 6.2 In `.github/workflows/push-image.yaml`, add `release: types: [published]` trigger alongside `push: branches: [main]`.
- [ ] 6.3 Add job-level `environment:` selector: `${{ github.event_name == 'release' && 'prod' || 'dev' }}`.
- [ ] 6.4 Add a build step that runs `npm run build -- --mode prod` only on the prod path (the existing dev build remains `npm run build`).
- [ ] 6.5 Set image tags conditionally per §3.4 pattern; prod gets `${tag}` and `${sha}`, dev keeps the existing triple.
- [ ] 6.6 Verify `tsc` + biome on the workflow + `.env.prod`.
- [ ] 6.7 Open frontend PR; review; merge.

## 7. Frontend: Cut prod Release (Phase 7 — operator-attended)

- [ ] 7.1 Tag `liverty-music/frontend:main` HEAD as `v1.0.0` (or matching backend's version).
- [ ] 7.2 Publish the GitHub Release.
- [ ] 7.3 Watch `gh run watch` for `push-image.yaml`; confirm `web-app:v1.0.0` pushed to `liverty-music-prod/frontend/`.
- [ ] 7.4 Pull the prod image locally; extract `/usr/share/caddy/index.html` and `assets/*.js`; verify:
  - No occurrences of `dev.liverty-music.app` in any chunk.
  - `api.liverty-music.app` appears in at least one chunk.
  - `auth.liverty-music.app` appears in at least one chunk.
  - The embedded OIDC `client_id` matches the value captured in §2.3.

## 8. Cloud-provisioning: Prod overlay image pinning + runbook (Phase 8 — `liverty-music/cloud-provisioning`)

- [ ] 8.1 In `k8s/namespaces/backend/overlays/prod/kustomization.yaml`, add an `images:` block pinning each of `server`, `consumer`, `concert-discovery`, `artist-image-sync` to `asia-northeast2-docker.pkg.dev/liverty-music-prod/backend/<name>:<sha-from-§5>`.
- [ ] 8.2 In `k8s/namespaces/frontend/overlays/prod/kustomization.yaml`, add an `images:` block pinning `web-app` to `asia-northeast2-docker.pkg.dev/liverty-music-prod/frontend/web-app:<sha-from-§7>`.
- [ ] 8.3 Run `kustomize build k8s/namespaces/backend/overlays/prod` and `... frontend/overlays/prod`; grep rendered Deployment images:
  - Every backend Deployment image SHALL match `^asia-northeast2-docker\.pkg\.dev/liverty-music-prod/backend/`.
  - The frontend Deployment image SHALL match `^asia-northeast2-docker\.pkg\.dev/liverty-music-prod/frontend/`.
  - No rendered image URI contains the substring `liverty-music-dev/`.
- [ ] 8.4 Add `docs/runbooks/revoke-cross-project-ar-iam.md` documenting the exact `gcloud projects remove-iam-policy-binding` invocation with a "MUST run AFTER overlay merge" guard.
- [ ] 8.5 Open cloud-provisioning PR; review; merge.

## 9. Cloud-provisioning: Verify ArgoCD prod cutover (Phase 9 — operator-attended)

- [ ] 9.1 Wait for ArgoCD to detect the cloud-provisioning main-branch change.
- [ ] 9.2 In ArgoCD UI / `kubectl --context=prod -n argocd get applications`, confirm `backend` and `frontend` apps reach `Synced/Healthy`.
- [ ] 9.3 `kubectl --context=prod -n backend get pod -o yaml | grep image:` — every image SHALL start with `liverty-music-prod/backend/`.
- [ ] 9.4 `kubectl --context=prod -n frontend get pod -o yaml | grep image:` — image SHALL start with `liverty-music-prod/frontend/`.
- [ ] 9.5 Curl smoke: `api.liverty-music.app/healthz` returns 401 (auth gate reachable); `auth.liverty-music.app/.well-known/openid-configuration` returns 200.

## 10. Operator: Revoke manual cross-project IAM grant (Phase 10)

- [ ] 10.1 Re-verify §9.3 and §9.4 — no pod still references a dev-AR image.
- [ ] 10.2 Run `gcloud projects remove-iam-policy-binding liverty-music-dev --member='serviceAccount:gke-node@liverty-music-prod.iam.gserviceaccount.com' --role='roles/artifactregistry.reader'`.
- [ ] 10.3 Wait 5 minutes; `kubectl --context=prod get pods -A | grep -E 'ImagePullBackOff|ErrImagePull'` — output SHALL be empty.
- [ ] 10.4 Verify via `gcloud projects get-iam-policy liverty-music-dev --flatten='bindings[].members' --filter='bindings.members~liverty-music-prod'` returns empty.

## 11. Operator: Prod ESC seeding (Phase 11)

- [ ] 11.1 Create a Slack notification channel for prod in GCP Console (Monitoring → Alerting → Edit notification channels → Slack). Record the channel ID.
- [ ] 11.2 `esc env set liverty-music/prod pulumiConfig.gcp.monitoring.slackNotificationChannels.alertBackend "<channel-id>"`.
- [ ] 11.3 `esc env set liverty-music/prod pulumiConfig.gcp.billingAlertEmail "pannpers@pannpers.dev"` (or the operator's preferred billing contact).
- [ ] 11.4 `esc env set liverty-music/prod pulumiConfig.gcp.budgetAmountJpy "10000"` (or operator-chosen prod budget; defaults to 3000 if unset).
- [ ] 11.5 `pulumi preview --stack prod`; confirm the diff shows MonitoringComponent + ZitadelMonitoringComponent + cost-budget + billing-alert-email creates.
- [ ] 11.6 `pulumi up --stack prod` (manual via Pulumi Cloud console).
- [ ] 11.7 Verify `gcloud monitoring channels list --project=liverty-music-prod` includes the new Slack channel + Google Chat + email channels.
- [ ] 11.8 Verify GCP Console → Billing → Budgets & Alerts shows the new prod budget.

## 12. Operator: Mainnet ticket SBT contract deployment (Phase 12)

- [ ] 12.1 Deploy the ticket SBT contract to Polygon mainnet (or the target EVM mainnet) using the prod deployer private key from `blockchain.deployerPrivateKey`. Record the deployed contract address.
- [ ] 12.2 Run the backend's existing SBT integration test against the deployed mainnet address; confirm `name()`, `symbol()`, `owner()`, `totalSupply()` respond correctly.
- [ ] 12.3 Open a cloud-provisioning PR updating the `TICKET_SBT_ADDRESS=` value in:
  - `k8s/namespaces/backend/overlays/prod/server/configmap.env`
  - `k8s/namespaces/backend/overlays/prod/consumer/configmap.env`
  - `k8s/namespaces/backend/overlays/prod/cronjob/concert-discovery/configmap.env`
- [ ] 12.4 Review + merge; ArgoCD picks up the new configmap; Reloader rolls server-app + consumer-app pods.
- [ ] 12.5 Verify via backend logs that the SBT client picks up the new contract address.

## 13. Operator: VAPID keypair verification + (if needed) regeneration (Phase 13)

- [ ] 13.1 Decrypt the prod `vapid-private-key` GSM secret: `gcloud secrets versions access latest --secret=vapid-private-key --project=liverty-music-prod`.
- [ ] 13.2 Derive the public point from the private key (Base64URL-encoded uncompressed P-256). Compare to `VAPID_PUBLIC_KEY` in `k8s/namespaces/backend/overlays/prod/server/configmap.env`.
- [ ] 13.3 If match (Mode A in design D9): record the no-op outcome; proceed to §14.
- [ ] 13.4 If mismatch (Mode B): generate a fresh prod VAPID keypair (`openssl ecparam -name prime256v1 -genkey -noout -out vapid-private.pem`; derive public point).
- [ ] 13.5 (Mode B only) `esc env set liverty-music/prod pulumiConfig.gcp.vapidPrivateKey "$(cat vapid-private.pem)" --secret`.
- [ ] 13.6 (Mode B only) Open a cloud-provisioning PR updating `VAPID_PUBLIC_KEY` in three backend configmaps + `frontend/.env.prod` `VITE_VAPID_PUBLIC_KEY`.
- [ ] 13.7 (Mode B only) Cut a frontend Release `v1.0.1` to rebuild with the new VAPID public key.
- [ ] 13.8 (Mode B only) Smoke: subscribe to push notifications via prod SPA; trigger a backend notification path; confirm browser receives the push without signature failure.

## 14. Operator: Verify blockchain mainnet values (Phase 13.5)

- [ ] 14.1 Decrypt `blockchain.rpcUrl` from prod ESC; verify it points at Polygon mainnet (no `amoy`/`mumbai`/`sepolia`/`testnet` substrings).
- [ ] 14.2 Decrypt `blockchain.deployerPrivateKey`; derive the Ethereum address; verify it equals the `owner()` of the mainnet SBT contract from §12.
- [ ] 14.3 Decrypt `blockchain.bundlerApiKey`; query the bundler's `chainId`; confirm it equals the mainnet chainId (137 for Polygon).
- [ ] 14.4 If any value is wrong, `esc env set liverty-music/prod pulumiConfig.blockchain.<key>` with the correct mainnet value.

## 15. Operator: Verify prod admin Google sub (Phase 13.5 continued)

- [ ] 15.1 Sign in to `https://auth.liverty-music.app/ui/console` with pannpers' Google account. The first sign-in attempt SHALL either succeed (sub matches what's in ESC) or fail with "user not found" (sub mismatch).
- [ ] 15.2 If sign-in fails, decrypt prod `zitadel.adminGoogleSubs.pannpers`; obtain the actual sub from the failed Zitadel IdP exchange logs or by listing the auto-created (unlinked) HumanUser in the admin org.
- [ ] 15.3 `esc env set liverty-music/prod pulumiConfig.zitadel.adminGoogleSubs.pannpers "<actual-sub>" --secret`.
- [ ] 15.4 `pulumi up --stack prod` to update the IdPLink resource.
- [ ] 15.5 Re-attempt sign-in; confirm success → IAM_OWNER role visible in Console.

## 16. Operator: Frontend prod preview artist content (Phase 13.5 continued, low priority)

- [ ] 16.1 Curate a prod-appropriate list of 11 artist UUIDs (sourced from prod DB) + 11 display names for `VITE_PREVIEW_ARTIST_IDS` / `VITE_PREVIEW_ARTIST_NAMES` in `frontend/.env.prod`.
- [ ] 16.2 Open a frontend PR with the curated list; cut the next Release (`v1.0.2`) to rebuild.

## 17. Operator: ESC stale field cleanup (Phase 14)

- [ ] 17.1 `grep -rn "zitadel.domain\|zitadel\.orgId\|pulumiJwtProfileJson" /home/pannpers/dev/src/github.com/liverty-music/` — confirm zero readers in any of the 4 repos.
- [ ] 17.2 `esc env rm liverty-music/prod pulumiConfig.zitadel.domain`.
- [ ] 17.3 `esc env rm liverty-music/prod pulumiConfig.zitadel.orgId`.
- [ ] 17.4 `esc env rm liverty-music/dev pulumiConfig.zitadel.domain`.
- [ ] 17.5 `esc env rm liverty-music/dev pulumiConfig.zitadel.orgId`.
- [ ] 17.6 `esc env rm liverty-music/dev pulumiConfig.zitadel.pulumiJwtProfileJson`.
- [ ] 17.7 `pulumi preview --stack dev` — expect zero diff (proof no reader).
- [ ] 17.8 `pulumi preview --stack prod` — expect zero diff.

## 18. Final: End-to-end prod smoke (Phase 15)

- [ ] 18.1 Visit `https://liverty-music.app/`; confirm SPA loads, no console errors, no `dev.liverty-music.app` requests in DevTools Network tab.
- [ ] 18.2 Sign up a new test user via prod SPA; confirm email verification email arrives (from `noreply@mail.liverty-music.app`).
- [ ] 18.3 Sign in the new test user; confirm OIDC redirect lands at `auth.liverty-music.app` and returns a JWT with the `email` claim.
- [ ] 18.4 Follow an artist; confirm the action persists (backend DB write).
- [ ] 18.5 Trigger a push notification via the operator console (or manual API call); confirm browser receives the push.
- [ ] 18.6 In GCP Console → Monitoring → Alerting, trigger a test alert (e.g., emit a fake ERROR log via `gcloud logging write`); confirm both the Slack channel and the Google Chat space receive the notification.
- [ ] 18.7 Confirm `kubectl --context=prod -n argocd get applications` shows all 14 apps `Synced/Healthy` (including `backend-migrations`).
- [ ] 18.8 Mark this change ready for `/opsx:archive`.
