## Why

Phase 3 needs a vetted-seller (Organizer) **tenancy foundation** before any
Organizer entity, console, or API can exist. Following Zitadel's official
B2B guidance (an Organization *is* the tenant), this change lays the static
Zitadel platform scaffolding and relaxes the pinned two-org topology so that
one Organization per Organizer can be provisioned at runtime later. This is
the first of four sub-changes decomposing roadmap step ①; grounded in
`docs/organizer-platform-design.md` and `docs/zitadel-tenancy-model.md`,
tracked by liverty-music/specification#759.

## What Changes

- Relax the Zitadel org topology so the instance may contain, besides the
  two IaC-managed platform orgs (`admin`, `liverty-music`), **runtime-
  provisioned Organizer tenant orgs** (one per Organizer) that are NOT
  IaC-managed and NOT treated as drift.
- Add a shared, **actor-named `organizer-console` Zitadel Project** owned by
  the `liverty-music` org, with the `master` ProjectRole and access-token
  role assertion enabled. Actor-named so a future `venue-console` never
  collides.
- Register the **`organizer-console` OIDC app** and a **`backend-api` app**
  on that project (the app audience the organizer API server will validate).
- Provision a dedicated **`organizer-provisioner` machine user** with
  instance-level org-create + cross-org grant rights (credential in
  ESC/Secret Manager), isolated from the existing single-org `backend-app`
  machine user.
- Define the **required login policy for Organizer tenant orgs**:
  passkey-only (`passwordlessType=ALLOWED`, `userLogin=false`,
  `allowRegister=false`, no Google IdP) with `allowDomainDiscovery=true`,
  set explicitly at provisioning — tenant orgs MUST NOT inherit the admin
  default (Google-IdP-only) policy.

Explicit non-goals (later sub-changes): the Organizer domain entity + admin
vetting + the runtime provisioning saga (`organizer-accounts`),
`organizer.html` + hosting (`organizer-console`), and the `api.organizer.*`
server + `OrganizerService.Get` + org-scoped authz (`organizer-rpc-server`).

## Capabilities

### New Capabilities
- `organizer-tenancy`: the shared `organizer-console` Zitadel project (its
  `master` role and apps), the `organizer-provisioner` machine user, and the
  required passkey-only + domain-discovery login policy that Organizer
  tenant orgs are provisioned with.

### Modified Capabilities
- `identity-management`: relax the "exactly two top-level orgs" topology to
  allow runtime-provisioned Organizer tenant orgs (one per Organizer).

## Impact

- **specification**: the `identity-management` topology delta + the new
  `organizer-tenancy` capability spec. **No proto/entity changes** (those
  land in `organizer-accounts`), so this change needs no BSR generation.
- **cloud-provisioning (IaC / Pulumi)**: the `organizer-console` project +
  `master` role + `organizer-console`/`backend-api` apps in the
  `liverty-music` org, and the `organizer-provisioner` machine user +
  credential.
- **backend / frontend**: none in this change.
