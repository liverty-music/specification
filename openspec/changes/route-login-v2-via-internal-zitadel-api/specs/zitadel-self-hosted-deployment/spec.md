## REMOVED Requirements

### Requirement: Login V2 UI Calls Zitadel API via Public URL

**Reason**: The "Gateway round-trip adds ~10ms" assumption did not hold in production. The Login V2 UI's server-side Connect-RPC call to `getAuthRequest` consistently hangs for 30 seconds when it traverses the public LB hairpin (`zitadel-web` Pod → GFE public IP → same Gateway → `zitadel-api`), surfacing as `504 upstream request timeout` to end users and blocking every sign-in and sign-up flow. Direct `wget` from the same Pod to the same URL responds in ~120 ms, isolating the failure to the Node.js HTTP client + GCP HTTPS LB hairpin combination — the same class of fault upstream Zitadel PR #12022 documented on Cloud Run as "intermittent SSL routines::record layer failure errors that were tenant-consistent". The hairpin design is therefore not viable.

**Migration**: Replaced by the new requirement `Login V2 UI Calls Zitadel API via Cluster-Internal URL` together with `Cluster-Internal Hostname Registered as InstanceCustomDomain` and `System API User Provisioned Declaratively via SystemAPIUsers Config`. The migration flips `ZITADEL_API_URL` to `http://zitadel-api.zitadel.svc.cluster.local:8080`, registers that hostname as an `InstanceCustomDomain` on the Zitadel instance, and provisions a Pulumi-managed System User to authorise the `AddCustomDomain` call. See `design.md` for the Pulumi resource dependency order.

## ADDED Requirements

### Requirement: Login V2 UI Calls Zitadel API via Cluster-Internal URL

The `zitadel-web` container SHALL set `ZITADEL_API_URL` to the cluster-internal Service URL of the Zitadel API (`http://zitadel-api.zitadel.svc.cluster.local:8080`), NOT the public issuer URL.

**Rationale**: The public-URL hairpin (`zitadel-web` Pod → public Gateway IP → same Gateway → `zitadel-api`) reliably hung Node.js Connect-RPC HTTP/1.1 calls for 30 seconds at the GFE record layer in prod, returning `504 upstream request timeout` to users and blocking every sign-in / sign-up. Routing intra-cluster traffic over the in-cluster Service avoids the GFE round-trip entirely. The Service hostname is unique per cluster and stable across Service IP reallocation, so this is robust to cluster operations that the prior `clusterIP`-pinning alternatives would not survive. The plaintext HTTP scheme is acceptable because traffic does not leave the cluster network; the existing `TLS Terminated at Gateway, Cluster Traffic Unencrypted` requirement already permits unencrypted in-cluster hops.

#### Scenario: Login UI Pod reaches Zitadel API via the cluster-internal Service hostname

- **WHEN** the `zitadel-web` Pod issues an outbound Connect-RPC call to fetch the auth request, instance settings, branding, or any other Zitadel API resource
- **THEN** the request URL SHALL be `http://zitadel-api.zitadel.svc.cluster.local:8080/...`
- **AND** the resulting `Host` header SHALL be `zitadel-api.zitadel.svc.cluster.local:8080`
- **AND** the request SHALL NOT traverse the public Gateway IP, the GCP HTTPS LB, or any external network hop

#### Scenario: Login UI configuration value does not reference the public URL

- **WHEN** the `zitadel-web` Deployment manifest (base and every overlay) is rendered
- **THEN** the `ZITADEL_API_URL` env value SHALL be the cluster-internal Service URL
- **AND** the value SHALL NOT be `https://auth.dev.liverty-music.app`, `https://auth.liverty-music.app`, or any other public hostname
- **AND** any per-environment overlay patch on this env var SHALL preserve the cluster-internal form

### Requirement: Cluster-Internal Hostname Registered as InstanceCustomDomain

The Zitadel instance in each environment SHALL have `zitadel-api.zitadel.svc.cluster.local` registered as an `InstanceCustomDomain`, declared as a Pulumi `zitadel.InstanceCustomDomain` resource and applied by the System User-authenticated Zitadel provider.

**Rationale**: Zitadel v4 matches the request's `Host` header against the instance's configured `InstanceDomains` to select a virtual instance; unmatched hosts return HTTP 404 before reaching any handler. The `Login V2 UI Calls Zitadel API via Cluster-Internal URL` requirement makes the Login UI's outbound calls carry `Host: zitadel-api.zitadel.svc.cluster.local:8080`, so the API must recognise that hostname. `InstanceCustomDomain` (not `InstanceTrustedDomain`) is required because only the former participates in `Host`-based routing; trusted domains affect OIDC discovery and email templates only.

#### Scenario: InstanceCustomDomain exists for both dev and prod

- **WHEN** querying the Zitadel `instance.v2.ListCustomDomains` API in either `dev` or `prod`
- **THEN** the response SHALL include an entry with `custom_domain: zitadel-api.zitadel.svc.cluster.local`
- **AND** the entry's `instance_id` SHALL match the bootstrapped instance ID of that environment

#### Scenario: Login UI SSR call is accepted by the API

- **WHEN** the `zitadel-web` Pod sends a Connect-RPC request to `http://zitadel-api.zitadel.svc.cluster.local:8080/zitadel.oidc.v2.OIDCService/GetAuthRequest` with a valid PAT
- **THEN** the Zitadel API SHALL return a 2xx response with the auth request body
- **AND** the API SHALL NOT return HTTP 404 with reason "instance not found"

#### Scenario: Pulumi declares the registration

- **WHEN** inspecting the Pulumi program for `dev` or `prod`
- **THEN** a `ZitadelInstanceCustomDomain` Pulumi Dynamic Resource SHALL exist with `customDomain: zitadel-api.zitadel.svc.cluster.local`
- **AND** the Dynamic Resource's `create` callback SHALL sign a System User JWT (`iss = sub = pulumi-system`, `aud = https://auth.<env>.liverty-music.app`) and call `instance.v2.InstanceService/AddCustomDomain` with that JWT as Bearer
- **AND** the resource SHALL NOT be implemented via the existing `@pulumiverse/zitadel.Provider` (which does not expose `InstanceCustomDomain` or a `system_api` auth block in v0.2.0)

### Requirement: System API User Provisioned Declaratively via SystemAPIUsers Config

The Zitadel API in each environment SHALL recognise a System User named `pulumi-system` (default membership `MemberType: System, Role: SYSTEM_OWNER`), provisioned by injecting a `ZITADEL_SYSTEMAPIUSERS` env value that references an RSA public key file. The corresponding RSA private key SHALL be generated by Pulumi (Node built-in `crypto.generateKeyPairSync`, RSA-2048), stored in the GSM Secret `zitadel-system-api-key` (PreservedTier), and consumed only by the `ZitadelInstanceCustomDomain` Pulumi Dynamic Resource for JWT signing.

**Rationale**: `instance.v2.AddCustomDomain` requires `system.domain.write` permission (its proto annotation explicitly says "cannot be called from an instance context"), which `IAM_OWNER` cannot satisfy. Zitadel has no escalation path from `IAM_OWNER` to `SYSTEM_OWNER`; they are disjoint scopes. The `SystemAPIUsers` config option lets a System User be declared purely by handing Zitadel a public key reference — no Console step, no first-instance DB-empty constraint, no imperative bootstrap. Pulumi-managed key generation keeps both halves of the keypair under infrastructure-as-code lifecycle control, and the PreservedTier secret tier ensures the key survives `workloadEnabled=false` dev shutdowns identically to `zitadel-masterkey`. The Pulumi wrapper `@pulumiverse/zitadel` does not expose a `system_api` provider auth block in v0.2.0, so a Pulumi Dynamic Resource signs JWTs directly using Node `crypto`.

#### Scenario: Private key is generated and stored

- **WHEN** Pulumi applies the cloud-provisioning stack for an environment
- **THEN** an RSA-2048 key pair SHALL be generated by Pulumi using the `@pulumi/tls.PrivateKey` resource (Pulumi-state-persisted, idempotent across re-applies)
- **AND** the private key SHALL be stored as a version of the GSM Secret `zitadel-system-api-key`
- **AND** the GSM Secret SHALL be classified as PreservedTier (survives `workloadEnabled=false` shutdown cycles)

#### Scenario: Public key reaches the Zitadel API Pod

- **WHEN** the `zitadel-api` Pod starts in `dev` or `prod`
- **THEN** the Pod's environment SHALL include `ZITADEL_SYSTEMAPIUSERS` referencing the System User name `pulumi-system` and the projected public key file path
- **AND** the public key SHALL be projected via ESO + K8s Secret + volume mount, mirroring the existing `external-secret-postgres-admin.yaml` pattern
- **AND** rotating the Pulumi-generated key pair SHALL trigger a Reloader-driven `zitadel-api` rollout that picks up the new public key

#### Scenario: Dynamic Resource consumes the private key only at create/refresh time

- **WHEN** inspecting the Pulumi program for `dev` or `prod`
- **THEN** the `ZitadelInstanceCustomDomain` Dynamic Resource's `create` and `read` callbacks SHALL receive the System User private key as a `pulumi.secret`-wrapped input
- **AND** the callbacks SHALL use only Node built-ins (`crypto`, `https`, `url`) to sign the JWT and call Zitadel — no external libraries that would break Pulumi dynamic-provider closure serialization
- **AND** the existing `pulumi-admin` IAM_OWNER `zitadel.Provider` SHALL remain unchanged and continue to own org / user / policy / OIDC-client resources
