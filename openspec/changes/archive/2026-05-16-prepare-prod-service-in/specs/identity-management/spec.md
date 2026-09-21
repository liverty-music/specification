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
