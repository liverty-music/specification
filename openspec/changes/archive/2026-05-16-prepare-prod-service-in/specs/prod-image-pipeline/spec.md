## ADDED Requirements

### Requirement: Frontend prod build SHALL bake env-prod values into the SPA bundle

The frontend Vite build that produces the prod container image SHALL load environment values from a prod-specific source (a `.env.prod` file at the repo root or an equivalent build-arg mechanism), not from the default `.env` file. The prod-specific source SHALL provide all `VITE_*` keys consumed by the SPA, with values pointing at prod-side endpoints (apex `liverty-music.app`, prod Zitadel issuer at `auth.liverty-music.app`, prod SPA OIDC client_id, prod product-org-id, prod VAPID public key, `info` log level), so the resulting bundle never references dev hostnames or dev identifiers.

#### Scenario: Prod build resolves API endpoints to prod hostnames

- **WHEN** searching the prod-built `web-app` container's static assets for the string `dev.liverty-music.app`
- **THEN** zero occurrences SHALL be found
- **AND** the strings `api.liverty-music.app` and `auth.liverty-music.app` SHALL each appear in at least one JS chunk

#### Scenario: Prod build uses prod SPA OIDC client_id

- **WHEN** decoding the bundled OIDC client configuration from the prod-built `web-app` static assets
- **THEN** `client_id` SHALL equal the `liverty-music` SPA `ApplicationOidc` client_id provisioned in the prod Zitadel `liverty-music` product org

#### Scenario: Prod build uses info-level logging

- **WHEN** decoding the bundled log configuration from the prod-built `web-app` static assets
- **THEN** the log level SHALL NOT equal `debug`
- **AND** SHALL be one of `info`, `warn`, or `error`

### Requirement: Backend prod image build SHALL be triggered by GitHub Release tags

The backend `deploy.yml` workflow SHALL build and push images to `liverty-music-prod/backend` Artifact Registry only when triggered by a published GitHub Release (i.e., a `release: types: [published]` event), not on push-to-`main`. The image SHALL be tagged with the release's tag (e.g., `v1.2.3`) and with the SHA of the commit at that tag. The existing dev path (push-to-`main` → push to `liverty-music-dev/backend`) SHALL be preserved unchanged.

#### Scenario: Push to main triggers dev-only build

- **WHEN** a commit is pushed to `liverty-music/backend:main`
- **THEN** the `deploy.yml` workflow SHALL push images only to `liverty-music-dev/backend/{server,consumer,concert-discovery,artist-image-sync}`
- **AND** SHALL NOT push to `liverty-music-prod/backend/*`

#### Scenario: GitHub Release publish triggers prod-only build

- **WHEN** a GitHub Release is published in `liverty-music/backend` with tag `vX.Y.Z`
- **THEN** the `deploy.yml` workflow SHALL push images to `liverty-music-prod/backend/{server,consumer,concert-discovery,artist-image-sync}`
- **AND** each pushed image SHALL carry the tag `vX.Y.Z` and the commit SHA at that tag

#### Scenario: Prod build uses prod environment Workload Identity

- **WHEN** the prod build path runs
- **THEN** GitHub Actions SHALL authenticate via the `prod` environment's Workload Identity Provider (`projects/108947861615/.../github-provider` and `github-actions@liverty-music-prod.iam.gserviceaccount.com`)

### Requirement: Frontend prod image build SHALL be triggered by GitHub Release tags

The frontend `push-image.yaml` workflow SHALL build with `.env.prod` (per the build-time env requirement above) and push to `liverty-music-prod/frontend/web-app` Artifact Registry only when triggered by a published GitHub Release. The image SHALL be tagged with the release's tag and with the commit SHA. The existing dev path SHALL be preserved.

#### Scenario: Push to main triggers dev-only frontend build

- **WHEN** a commit is pushed to `liverty-music/frontend:main`
- **THEN** the workflow SHALL push only to `liverty-music-dev/frontend/web-app`
- **AND** SHALL NOT push to `liverty-music-prod/frontend/web-app`

#### Scenario: GitHub Release publish triggers prod frontend build

- **WHEN** a GitHub Release is published in `liverty-music/frontend` with tag `vX.Y.Z`
- **THEN** the workflow SHALL push to `liverty-music-prod/frontend/web-app`
- **AND** the image SHALL carry tag `vX.Y.Z` and the commit SHA
- **AND** the build SHALL have consumed `.env.prod` (asserted via the bake-time invariant in the build-bake requirement above)
