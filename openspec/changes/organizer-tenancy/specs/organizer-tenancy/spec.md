## Purpose

The static Zitadel platform scaffolding for the Organizer B2B tenancy model:
a shared, actor-named `organizer-console` project (roles + apps) owned by the
product org, a dedicated provisioner machine user, and the login policy that
runtime-provisioned Organizer tenant orgs must receive. Per-Organizer orgs,
the domain entity, the console, and the API server are separate changes.

## ADDED Requirements

### Requirement: Shared organizer-console project in the product org

The system SHALL provision, via IaC, a single actor-named
**`organizer-console`** Zitadel Project owned by the `liverty-music` product
org, defining a **`master`** ProjectRole and enabling access-token role
assertion so operator tokens carry the `organizer-console` project roles.
The project SHALL be shared to Organizer tenant orgs via Project Grant (the
grant itself is created at runtime, not by IaC). Roles for a future
sub-owner model are out of scope; only `master` is defined now. The project
name is actor-qualified so a future `venue-console` project does not
collide.

#### Scenario: Organizer-console project exists in the product org

- **WHEN** the Pulumi stack is applied
- **THEN** an `organizer-console` Zitadel Project SHALL exist owned by the
  `liverty-music` org
- **AND** it SHALL define a `master` ProjectRole
- **AND** access-token role assertion SHALL be enabled so operator tokens
  carry the project roles claim

#### Scenario: Role check does not block sign-in

- **WHEN** an operator without a granted role signs in
- **THEN** the project SHALL NOT block the login on a missing grant
  (authorization is enforced at the backend), keeping the login flow
  resilient

### Requirement: Organizer console OIDC app and backend API app

The system SHALL register, via IaC, an **`organizer-console` OIDC
application** (PKCE, no client secret) and a **`backend-api` application**
on the `organizer-console` project. The OIDC app is the single client that
serves all Organizer tenants; the API app is the audience the organizer API
server validates. The OIDC app SHALL carry the organizer console redirect
URIs for each environment.

#### Scenario: OIDC app serves all tenants with per-env redirect URIs

- **WHEN** the Pulumi stack is applied for an environment
- **THEN** an `organizer-console` OIDC application SHALL exist on the
  project with PKCE and no client secret
- **AND** its redirect URIs SHALL include the organizer console host for
  that environment
- **AND** a single OIDC app SHALL serve operators of any Organizer tenant
  org (no per-tenant app)

#### Scenario: Backend API app provides the audience

- **WHEN** the Pulumi stack is applied
- **THEN** a `backend-api` application SHALL exist on the
  `organizer-console` project so its project id can be requested into the
  access-token audience by the organizer console

### Requirement: Dedicated organizer-provisioner machine user

The system SHALL provision, via IaC, a dedicated **`organizer-provisioner`**
machine user holding the narrowest instance-level role that permits creating
organizations and cross-org Project Grants and User Grants, separate from
the existing single-org `backend-app` machine user, with its credential
stored in ESC / Secret Manager. This user is the credential the backend uses
at runtime to provision Organizer tenant orgs.

#### Scenario: Provisioner machine user exists with org-create rights

- **WHEN** the Pulumi stack is applied
- **THEN** an `organizer-provisioner` machine user SHALL exist with
  instance-level rights to create organizations and cross-org grants
- **AND** it SHALL be distinct from the `backend-app` machine user (blast
  radius isolation)
- **AND** its credential SHALL be stored in ESC / Secret Manager, not in
  source

### Requirement: Organizer tenant orgs use a passkey-only login policy with domain discovery

Every runtime-provisioned Organizer tenant org SHALL be given an **explicit**
login policy — it SHALL NOT inherit the instance default (admin
Google-IdP-only) policy. The policy SHALL be **passkey-only**
(`passwordlessType=ALLOWED`, `userLogin=false`, `allowRegister=false`, no
external/Google IdP) with **`allowDomainDiscovery=true`** so an operator is
routed to their own org by their email domain at login. (Applying this
policy to each org happens in the runtime provisioning flow of
`organizer-accounts`; this requirement defines the required shape.)

#### Scenario: A provisioned tenant org has the passkey-only policy

- **WHEN** an Organizer tenant org is provisioned
- **THEN** it SHALL have an explicitly set login policy, not the inherited
  admin default
- **AND** the policy SHALL be passkey-only (`passwordlessType=ALLOWED`,
  `userLogin=false`, `allowRegister=false`, no Google IdP)
- **AND** `allowDomainDiscovery` SHALL be enabled

#### Scenario: Operator is routed to their org by email domain

- **WHEN** an operator enters their email on the organizer console login
- **THEN** domain discovery SHALL route them to their own Organizer tenant
  org's login policy without an org picker
