## ADDED Requirements

### Requirement: Dedicated container image and Kubernetes workload

The admin console SHALL be served from its own container image and its own
Kubernetes Deployment and Service, independent of the consumer SPA workload. The
consumer SPA's image, Deployment, Caddy configuration, and config delivery MUST
remain unchanged. A change to the admin workload MUST NOT trigger a restart or
redeploy of the consumer SPA workload.

#### Scenario: Independent workloads

- **WHEN** the admin console is deployed
- **THEN** it runs as a separate Deployment/Service and the consumer SPA
  Deployment is not modified or restarted by the admin deployment

#### Scenario: Isolated config reload

- **WHEN** the admin runtime config changes and triggers a rollout of the admin
  workload
- **THEN** only the admin pod restarts; the consumer SPA pod is unaffected

### Requirement: Dedicated hostname on the shared external gateway

The admin console SHALL be reachable at `admin.{env-base-domain}` (e.g.
`admin.dev.liverty-music.app`, `admin.liverty-music.app`) via a dedicated
HTTPRoute attached to the shared external gateway, routing that hostname to the
admin Service. The consumer hostname's routing MUST remain unchanged.

#### Scenario: Admin hostname routes to admin workload

- **WHEN** a request arrives for the admin hostname
- **THEN** the shared gateway routes it to the admin Service

#### Scenario: Consumer hostname unaffected

- **WHEN** a request arrives for the consumer hostname
- **THEN** it continues to route to the consumer SPA Service unchanged

### Requirement: Per-host runtime config delivery

The admin pod SHALL serve its own `/config.json` at the canonical path,
containing the admin org id and the admin OIDC client id, mounted per environment
as a Kubernetes ConfigMap. The admin console MUST resolve its runtime
configuration from the canonical `/config.json` path without altering the shared
config-loading contract used by the consumer SPA.

#### Scenario: Admin receives admin configuration

- **WHEN** the admin console fetches `/config.json` at boot
- **THEN** it receives the admin org id and admin client id for the current
  environment

#### Scenario: Shared config contract preserved

- **WHEN** the admin console boots
- **THEN** it uses the same `/config.json` canonical path and loader contract as
  the consumer SPA, with no host-conditional rewrite of the config path

### Requirement: Admin-org OIDC application provisioning

A Zitadel `ApplicationOidc` SHALL be provisioned in the `admin` org as a public
SPA client (PKCE, no secret) with redirect URIs at
`https://admin.{env-base-domain}/auth/callback` and matching post-logout redirect
URIs per environment. It SHALL be a distinct resource from the consumer
`web-frontend` application, leaving the consumer application and product-org
login policy unchanged.

#### Scenario: Admin OIDC app exists per environment

- **WHEN** infrastructure is provisioned for an environment
- **THEN** an admin-org `ApplicationOidc` exists with that environment's admin
  redirect and post-logout URIs

#### Scenario: Consumer application untouched

- **WHEN** the admin OIDC application is provisioned
- **THEN** the consumer `web-frontend` application and the product-org login
  policy are not modified

### Requirement: TLS certificate and DNS for the admin hostname

The admin hostname SHALL be covered by a managed TLS certificate via the gateway
certmap and SHALL resolve via Cloud DNS for each environment, before the admin
HTTPRoute begins serving production traffic.

#### Scenario: Admin hostname is reachable over TLS

- **WHEN** the admin hostname is requested over HTTPS
- **THEN** it presents a valid managed certificate and resolves to the gateway

### Requirement: GitOps delivery for the admin image

The admin image SHALL be published to Artifact Registry and reconciled through
the existing ArgoCD image-updater automation as its own tracked artifact, so the
admin console releases independently of the consumer SPA.

#### Scenario: Admin image is auto-reconciled

- **WHEN** a new admin image digest is published to Artifact Registry
- **THEN** ArgoCD image-updater updates the admin workload to that digest without
  affecting the consumer SPA's tracked image
