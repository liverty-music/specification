## 1. frontend: the preview address chooses the API address (components/infrastructure/fan/web/global/app-shell)

- [ ] 1.1 Map `preview.liverty-music.app` to `prod` in `shared/config/known-hosts.ts`, and make the loader in `shared/config/app-config.ts` return `https://api.preview.liverty-music.app` as the API address when the page host is exactly `preview.liverty-music.app` (design D3). Verify with unit tests, each annotated with `@spec`, covering all four scenarios of "The fan web app served from the preview address calls the preview API": loaded from the preview address, loaded from the production address, production configuration on the preview address, other environment's configuration on the preview address.
- [ ] 1.2 Cut a frontend release containing 1.1 and confirm the production site still loads and calls `https://api.liverty-music.app` (open it, read the network requests in Playwright against the deployed app), so the change is proven inert before any preview exists.

## 2. cloud-provisioning: Argo Rollouts controller

- [ ] 2.1 Add the Argo Rollouts controller as a namespace (`k8s/namespaces/argo-rollouts/`, a pinned Helm chart rendered by Kustomize, registered the way the `keda` namespace is), with small resource requests matching the other controllers, in the prod overlay only. Verify: `kubectl get deploy -n argo-rollouts` shows it available and ArgoCD reports the Application Healthy.

## 3. cloud-provisioning: preview hostnames (design D2)

- [ ] 3.1 Add `fan-preview-web` (`preview`) and `fan-preview-api` (`api.preview`) to the service catalog in `src/gcp/components/network.ts`, production only. Verify: `pulumi preview` on the prod stack lists the DNS record, DnsAuthorization, Certificate and CertificateMapEntry for each and nothing else; a unit test of the catalog covers both hostnames in prod and none in dev.
- [ ] 3.2 After the owner runs the prod `pulumi up`, confirm both certificates are ACTIVE (`gcloud certificate-manager certificates describe`, read-only, `--configuration=liverty-music`) and both names resolve to the Gateway address.

## 4. cloud-provisioning: sign-in and CORS accept the preview address (design D4)

- [ ] 4.1 Add the preview address's callback, passkey-callback and post-logout addresses to the fan application in `src/zitadel/components/frontend.ts` for production only. Verify with the Pulumi unit test for the component (production includes them, dev does not) and a clean `pulumi preview`.
- [ ] 4.2 Add `https://preview.liverty-music.app` to `CORS_ALLOWED_ORIGINS` in the production fan-api ConfigMap. Verify: `kustomize build` of the prod overlay shows the list with both origins, and after sync a `curl` preflight from the preview origin to `https://api.liverty-music.app` is answered with that origin allowed.

## 5. cloud-provisioning: `fan-web` released through a Rollout (design D1, D5, D6, D7)

- [ ] 5.1 In the prod overlay add a `Rollout` for `fan-web` (`workloadRef` to the base Deployment, `blueGreen`, `autoPromotionEnabled: false`, `previewReplicaCount: 1`, `scaleDownDelaySeconds`), an active and a preview Service, and an HTTPRoute for `preview.liverty-music.app` to the preview Service, with the backend and health-check policies the existing Service has. Verify: `kustomize build` succeeds for prod and dev, dev output is unchanged, and the Rollout reaches Healthy on the unchanged pin.
- [ ] 5.2 Run a release through it: bump the pin, confirm the Rollout pauses with the new Pods on the preview Service, run `SMOKE_BASE_URL=https://preview.liverty-music.app` through the frontend smoke spec, then promote. Record which promote command works (`kubectl argo rollouts promote` or the Argo CD resource action); if the plugin is needed, add it to the cloud-provisioning mise config. Verify: the smoke spec passes on preview, `https://liverty-music.app` serves the old release until promotion and the new one after.
- [ ] 5.3 Check whether ArgoCD reports the Services OutOfSync because of the selector hash while the Rollout is paused (`argocd app get`); if it does, add an `ignoreDifferences` entry for `/spec/selector` on those Services. Verify: the Application stays Synced and Healthy-or-Suspended during the pause.
- [ ] 5.4 Add the check-then-promote procedure to `docs/runbooks/prod-image-tag-pinning.md`: look at `kubectl get rollout` after every pin bump, the read-only commands an agent runs, the owner-only account used on preview and deleting its push subscription afterwards, promote, abort with the pin revert, and the migration rule (backward compatible, design Risks). Verify: the runbook's commands, run as written against the 5.2 release, produce the outputs it describes.

## 6. cloud-provisioning: `fan-api` released through a Rollout (design D1, D2, D7)

- [ ] 6.1 Do 5.1 for `fan-api`: a `Rollout`, active and preview Services with the existing backend and health-check policies, and an HTTPRoute for `api.preview.liverty-music.app` that routes only the fan API's server port and never `fan-api-webhook-svc`. Verify: `kustomize build` for prod and dev (dev unchanged); `curl https://api.preview.liverty-music.app/stripe-webhook` and the Zitadel action paths do not reach the webhook server.
- [ ] 6.2 Run a release through it: confirm the pause, `curl` the preview API's health and one read RPC, and promote. Verify: fans' address serves the old API until promotion, with no failed request while the selector switches (a loop of requests against `https://api.liverty-music.app` across the promote shows none).
- [ ] 6.3 Extend the runbook with the API checks and the API-then-web promotion order for a release that changes both. Verify: the commands run as written against the 6.2 release.

## 7. Integration

- [ ] 7.1 Release a trivial version of both workloads together; check both previews, promote API then web, and confirm both serve fans. Verify: `kubectl get rollout` shows both Healthy on the new revision and the production smoke spec passes on `https://liverty-music.app`.
- [ ] 7.2 On preview, sign in with the owner's account with an existing passkey (the inference in design D4), open a signed-in screen, and sign out. Verify: the hosted login completes and returns to `https://preview.liverty-music.app/`; record the result in the PR. If it fails, the passkey inference is wrong and the design is revised before promotion becomes routine.
- [ ] 7.3 Abort one release on purpose. Verify: fans never see it, `kubectl get rollout` returns to the previous revision, and the pin revert restores `main`.
