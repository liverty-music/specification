## MODIFIED Requirements

### Requirement: Manage OIDC Application

The system SHALL manage the OIDC application for the frontend SPA within
the `liverty-music` project (in the `liverty-music` product org) to enable
end-user authentication.

#### Scenario: Provision OIDC App in product org

- **WHEN** Pulumi stack is applied
- **THEN** an OIDC application named `liverty-music` SHALL exist in the
  `liverty-music` project
- **AND** the application Type SHALL be "SPA"
- **AND** the Auth Method Type SHALL be "NONE"
- **AND** the application's `client_id` SHALL be committed to the
  frontend repo's build-time environment file for that env (`.env` for
  the dev build pipeline, `.env.prod` for the prod build pipeline —
  see the `prod-image-pipeline` capability) alongside the owning org's
  id as `VITE_ZITADEL_ORG_ID`, so each env's build embeds its own
  identifiers into the SPA bundle by Vite and bakes them into the
  `web-app` container image. There is intentionally no separate
  "frontend" Pulumi stack consuming the value via ESC — the build-time
  embedding model is simpler and matches Vite's `import.meta.env.VITE_*`
  convention. Each env's build pipeline selects its own env file via the
  release-tag-triggered workflow.

#### Scenario: Prod build embeds prod identifiers

- **WHEN** the prod frontend build runs (triggered by a GitHub Release in `liverty-music/frontend`)
- **THEN** the resulting `web-app:vX.Y.Z` image SHALL embed `VITE_ZITADEL_CLIENT_ID` equal to the `liverty-music` `ApplicationOidc` `client_id` in the **prod** Zitadel `liverty-music` product org
- **AND** SHALL embed `VITE_ZITADEL_ORG_ID` equal to the prod `liverty-music` product org id
- **AND** SHALL NOT embed any dev identifiers (no dev client_id, no dev org_id)

## ADDED Requirements

### Requirement: Maintain Google OAuth Client in Prod Infrastructure

The system SHALL maintain a Google Cloud OAuth 2.0 Web Application
client in the `liverty-music-prod` GCP project (the same project that
hosts the prod GKE cluster, Cloud SQL instance, and Zitadel workload).
The client's authorised redirect URI MUST point at the prod Zitadel
Login V2 IdP callback path (`https://auth.liverty-music.app/idps/callback`).
The client's `client_id` and `client_secret` MUST be present in Pulumi
ESC under `liverty-music/prod` and MUST never be committed to git.

This is the prod sibling of the existing "Maintain Google OAuth Client
in Dev Infrastructure" requirement; the same operational pattern
(manual GCP Console creation → `esc env set`) applies.

#### Scenario: OAuth client exists with correct redirect URI

- **WHEN** an operator inspects the `liverty-music-prod` GCP project
  Credentials page
- **THEN** a Google OAuth 2.0 Web Application client SHALL exist with
  the application name "Zitadel Admin IdP (prod)" (or equivalent)
- **AND** its authorised redirect URI SHALL include
  `https://auth.liverty-music.app/idps/callback`

#### Scenario: ESC carries the prod credentials

- **WHEN** Pulumi stack `prod` is previewed or applied
- **THEN** ESC `liverty-music/prod` SHALL resolve
  `pulumiConfig.zitadel.googleAdminIdp.clientId` to the prod OAuth
  client's client_id (plaintext, prefixed by the prod project number
  `108947861615-`)
- **AND** SHALL resolve `pulumiConfig.zitadel.googleAdminIdp.clientSecret`
  to the prod OAuth client's client_secret, marked as encrypted

#### Scenario: Dev and prod clients are distinct

- **WHEN** comparing the prod `googleAdminIdp.clientId` to the dev
  `googleAdminIdp.clientId`
- **THEN** the values SHALL be different
- **AND** the prod client SHALL be owned by GCP project number
  `108947861615` (prod), not `1058199000631` (dev)

#### Scenario: No prod OAuth secret in git

- **WHEN** the repository is searched for the prod OAuth client secret value
- **THEN** the secret SHALL NOT appear in any committed file in
  `cloud-provisioning`, `specification`, `backend`, or `frontend`

#### Scenario: Client recreation runbook covers prod

- **WHEN** the prod OAuth client is accidentally deleted in the Google
  Cloud Console
- **THEN** the cloud-provisioning runbook (`docs/runbooks/zitadel-oauth-client-recreate.md`)
  SHALL document the manual recreation steps for the prod project
  (Internal consent screen → Web application client → prod redirect
  URI → `esc env set liverty-music/prod`)
- **AND** following the runbook SHALL restore the prod admin Google
  sign-in flow without any spec change
