# Workload Naming Convention

## Purpose

Establish a single, derivable naming convention for platform workloads and every
resource bound to them (Kubernetes objects, GCP identities, image repositories,
routes, secrets), so that from an application's audience alone an operator or tool
can predict all of its related resource names, and so future workloads are named
without re-litigation.

## Requirements

### Requirement: Workload names follow the audience-tier scheme

Every deployable workload SHALL be named `<audience>-<tier>`, where `<audience>` is
one of `fan`, `admin-console`, or `organizer-console`, and `<tier>` is one of `web`
(browser bundle served to that audience), `api` (Connect-RPC server for that
audience), or `event-consumer` (JetStream event worker). The audience SHALL match the
proto RPC audience segment (`rpc.<audience>.*`, where the consumer/fan audience is the
unprefixed default). No workload SHALL use an ad-hoc suffix such as `-app`.

#### Scenario: Deriving a workload name from its audience and tier

- **WHEN** a reader needs the name of the fan-facing Connect-RPC server
- **THEN** it SHALL be `fan-api`, the fan browser bundle SHALL be `fan-web`, the admin
  console API SHALL be `admin-console-api`, the admin console bundle SHALL be
  `admin-console-web`, and the organizer console API/bundle SHALL be
  `organizer-console-api` / `organizer-console-web`

#### Scenario: The JetStream worker uses the event-consumer tier

- **WHEN** the platform runs a single cross-domain JetStream event worker
- **THEN** it SHALL be named `event-consumer` (a future per-entity split MAY prefix the
  entity, e.g. `concert-event-consumer`, but SHALL keep the `-event-consumer` tier)

#### Scenario: No legacy ad-hoc suffixes remain

- **WHEN** the platform's workloads are enumerated after migration
- **THEN** none SHALL be named `server-app`, `web-app`, `admin-app`, `organizer-app`,
  or `consumer-app`

### Requirement: Derived resources share the workload stem with uniform suffixes

Every Kubernetes resource bound to a workload SHALL reuse the workload name as its
stem with a uniform suffix: Service `<stem>-svc`, HealthCheckPolicy `<stem>-policy`,
HTTPRoute `<stem>-route`, ExternalSecret `<stem>-secrets`, and configmap `<stem>-config`.
Env-specific hostnames on HTTPRoutes SHALL remain unchanged by the rename (they are the
external contract).

#### Scenario: Deriving bound resource names for a workload

- **WHEN** the workload is `fan-api`
- **THEN** its Service SHALL be `fan-api-svc`, its HTTPRoute `fan-api-route`, its
  HealthCheckPolicy `fan-api-policy`, and any dedicated ExternalSecret
  `fan-api-secrets`

#### Scenario: The admin console ExternalSecret conforms

- **WHEN** the admin console API's dedicated secret is rendered after migration
- **THEN** it SHALL be named `admin-console-api-secrets` (not `admin-console-secrets`)

### Requirement: GCP identities and image repositories key off the same principal

A workload's GCP identity SHALL use the workload name as the principal: the Google
Service Account account-id SHALL be `<stem>`, its Cloud SQL IAM database user SHALL be
`<stem>@<project>.iam`, its Zitadel MachineKey GSM secret SHALL be
`zitadel-machine-key-for-<stem>`, and its Artifact Registry image repository SHALL be
`<layer>/<stem>` (layer ∈ `backend` / `frontend`). Workload Identity and per-secret IAM
bindings SHALL reference that principal.

#### Scenario: Deriving GCP identity names for a workload

- **WHEN** the fan-facing API workload `fan-api` is provisioned
- **THEN** its GSA account-id SHALL be `fan-api`, its Cloud SQL IAM user SHALL be
  `fan-api@<project>.iam`, its image repo SHALL be `backend/fan-api`, and its Zitadel
  MachineKey secret SHALL be `zitadel-machine-key-for-fan-api`

### Requirement: A canonical name mapping is the authoritative reference

This capability SHALL maintain a canonical mapping from each current workload to its
target name so that the migration and all downstream references resolve to a single
source of truth.

#### Scenario: The mapping enumerates every platform workload

- **WHEN** an operator consults the convention for a workload's canonical name
- **THEN** the mapping SHALL cover at least: `server-app`→`fan-api`,
  `web-app`→`fan-web`, `consumer-app`→`event-consumer`, `admin-app`→`admin-console-web`
  (`admin-console-api` unchanged), and `organizer-app`→`organizer-console-web`
  (`organizer-console-api` built new), plus each workload's derived Kubernetes, GCP
  identity, image, and secret names

### Requirement: Renames use an additive create-new then cutover then delete-old migration

Renaming a live workload or a state-tracked / route-bound resource SHALL follow a
create-new → cutover → delete-old sequence rather than an in-place rename, so that
Gateway routes, Pulumi/Cloud SQL/IAM state, and ArgoCD-managed resources move without a
stuck-replace or dependency cascade. A brief per-service interruption during cutover is
acceptable; external hostnames SHALL NOT change.

#### Scenario: Renaming a route-bound backend workload

- **WHEN** `server-app` is renamed to `fan-api`
- **THEN** the new `fan-api` Deployment/Service/route SHALL be created and the HTTPRoute
  hostname (`api.liverty-music.app`) SHALL be repointed to it before the old `server-app`
  resources are deleted, leaving the external hostname unchanged

#### Scenario: Future workloads are named from the convention at creation

- **WHEN** a new workload is introduced (e.g. the organizer console API)
- **THEN** it SHALL be created directly under its canonical name (`organizer-console-api`)
  with no later rename required
