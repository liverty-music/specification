## MODIFIED Requirements

### Requirement: Manage Zitadel Organization

The system SHALL manage Zitadel organization topology so that the instance
always exposes a clear separation between operator (admin), product, and
Organizer-tenant identities. The instance SHALL contain **two IaC-managed
platform organizations**, plus **one runtime-provisioned Organizer tenant
organization per vetted Organizer**:

- An **`admin`** role org, created by Zitadel at first-instance bootstrap
  via the configmap setting `ZITADEL_FIRSTINSTANCE_ORG_NAME=admin`,
  brought into Pulumi state via a one-time `pulumi import
  zitadel:index/org:Org admin <admin-org-id>` (see Migration Plan in
  design.md), and pinned with `protect: true`. This org holds operator
  identities only (machine users used by IaC and the Login V2 service,
  plus human admins who manage the instance) and is the **Zitadel
  default org** so that the Console (which omits `org_id` in its OIDC
  AuthN) routes to its `LoginPolicy`.

- A **`liverty-music`** product org, created by Pulumi as a `zitadel.Org`
  resource with `isDefault: false`. This org holds the product Project,
  applications, end-user login policy, and end-user accounts. The
  frontend SPA's `ApplicationOidc` carries an explicit `client_id`
  whose owning org Zitadel resolves to `liverty-music`, so the
  default-org choice does not affect end-user OIDC routing. This org also
  owns the actor-named **`organizer-console`** Project (its roles and
  apps), which is Project-Granted to each Organizer tenant org.

- **Organizer tenant orgs** — one per vetted Organizer, **provisioned at
  runtime via the Zitadel Management API** when an admin vets an Organizer
  (from the admin console → backend, using a machine-user credential), NOT
  IaC-managed. Each isolates one Organizer's operator identities and
  receives a Project Grant to the `liverty-music` org's `organizer-console`
  project. See `docs/zitadel-tenancy-model.md`.

#### Scenario: Provision admin role org via bootstrap + import

- **WHEN** the Zitadel instance bootstraps for the first time in any
  environment
- **THEN** the configmap SHALL set `ZITADEL_FIRSTINSTANCE_ORG_NAME=admin`
- **AND** Zitadel SHALL create an organization named `admin` containing
  the `pulumi-admin` machine user
- **AND** an operator SHALL run `pulumi import zitadel:index/org:Org
  admin <admin-org-id>` (with `--provider liverty-music-provider=...`)
  to bring the admin org into Pulumi state
- **AND** the Pulumi declaration SHALL set `isDefault: true` and
  `{ protect: true }` on the admin org
- **AND** no Pulumi rename step SHALL be required to reach the intended
  name

#### Scenario: Provision product org via Pulumi

- **WHEN** Pulumi stack is applied
- **THEN** a `zitadel.Org` resource named `liverty-music` SHALL exist
  with `isDefault: false`
- **AND** all product resources (Project, ApplicationOidc, end-user
  LoginPolicy, end-user HumanUsers) SHALL live in this org
- **AND** the `organizer-console` Project (its roles and apps) SHALL also
  live in this org

#### Scenario: Console login routes to the admin org's policy

- **WHEN** an operator opens
  `https://auth.dev.liverty-music.app/ui/console`
- **THEN** the Zitadel Console's OIDC AuthN SHALL hit Login V2 without
  an explicit `org_id`
- **AND** Login V2 SHALL render the **default org's `LoginPolicy`**,
  which is the admin org's policy (Google IdP enabled,
  `userLogin = false`)
- **AND** the operator SHALL see a "Sign in with Google" button
  immediately, without needing to type a username first

#### Scenario: No third org

- **WHEN** the instance is fully provisioned
- **THEN** exactly two IaC-managed platform orgs SHALL exist (`admin` and
  `liverty-music`) — no third *IaC-managed* org
- **AND** any additional organization SHALL exist only as a
  runtime-provisioned Organizer tenant org (one per vetted Organizer),
  created via the Zitadel Management API
- **AND** such runtime-provisioned Organizer tenant orgs SHALL NOT be
  treated as Pulumi drift or reverted on apply

#### Scenario: Admin org cannot be accidentally destroyed

- **WHEN** any operator runs `pulumi destroy` against the dev stack
- **THEN** Pulumi SHALL refuse to remove the `admin` org because of
  `protect: true`
- **AND** removing the protection SHALL require a code change in a
  reviewable PR
- **AND** this protection SHALL prevent the cascading loss of the
  `pulumi-admin` machine user, which would lock the
  `@pulumiverse/zitadel` provider out of the instance
