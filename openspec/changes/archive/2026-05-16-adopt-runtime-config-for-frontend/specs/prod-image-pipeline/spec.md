# prod-image-pipeline Specification

## REMOVED Requirements

### Requirement: Frontend prod build SHALL bake env-prod values into the SPA bundle

**Reason**: Build-time env baking is structurally fragile (it caused the v1.0.0 blank-screen Sev-1 by interacting with `@aurelia/vite-plugin`'s literal `mode === 'production'` check) and produces per-environment images whose runtime behavior cannot be verified against a single artifact. The new model fetches `/config.json` at bootstrap from a per-environment K8s ConfigMap, eliminating build-time env divergence entirely.

**Migration**: Per-environment values move out of `frontend/.env.prod` (deleted) and into `cloud-provisioning/k8s/namespaces/frontend/overlays/<env>/configmap.yaml`. The frontend image SHALL be built with no env-specific build-args. See the new `frontend-runtime-config` capability for the runtime config contract and the new ADDED requirement below for the env-agnostic bundle invariant.

## MODIFIED Requirements

### Requirement: Frontend prod image build SHALL be triggered by GitHub Release tags

The frontend `push-image.yaml` workflow SHALL build and push to `liverty-music-prod/frontend/web-app` Artifact Registry only when triggered by a published GitHub Release. The build SHALL be env-agnostic (per the "Frontend prod image SHALL be env-agnostic at the bundle level" requirement) — the same Dockerfile inputs are used whether the workflow's trigger is `push: branches: [main]` (dev path) or `release: types: [published]` (prod path). The image SHALL be tagged with the release's tag and with the commit SHA. The existing dev path (push-to-main → `liverty-music-dev/frontend/web-app:latest,:<sha>`) SHALL be preserved.

#### Scenario: Push to main triggers dev-only frontend build

- **WHEN** a commit is pushed to `liverty-music/frontend:main`
- **THEN** the workflow SHALL push only to `liverty-music-dev/frontend/web-app`
- **AND** SHALL NOT push to `liverty-music-prod/frontend/web-app`

#### Scenario: GitHub Release publish triggers prod frontend build

- **WHEN** a GitHub Release is published in `liverty-music/frontend` with tag `vX.Y.Z`
- **THEN** the workflow SHALL push to `liverty-music-prod/frontend/web-app`
- **AND** the image SHALL carry tag `vX.Y.Z` and the commit SHA

#### Scenario: Prod and dev builds use identical Dockerfile inputs

- **WHEN** comparing the `docker build` invocations of the dev push path and the release prod path
- **THEN** neither invocation SHALL pass a `--build-arg VITE_MODE` (or any other env-specific build-arg)
- **AND** the Dockerfile evaluation SHALL produce functionally identical `/srv/*` content for both paths, modulo timestamps and other non-deterministic build metadata

#### Scenario: Post-build template-presence assertion gates both paths

- **WHEN** either the dev push path or the release prod path runs `npm run build`
- **THEN** a post-build assertion step SHALL run `scripts/verify-build-templates.ts` (or equivalent)
- **AND** the step SHALL fail the workflow if any route chunk under `dist/assets/*-route-*.js` does not contain its expected template-derived marker string
- **AND** the workflow SHALL refuse to push the image if the assertion fails
