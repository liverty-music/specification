## Why

With the Zitadel tenancy foundation in place (`organizer-tenancy`), this
change adds the **Organizer domain** — the vetted seller an admin creates,
its link to the artists it represents, and the runtime provisioning that
gives each Organizer an isolated Zitadel tenant its operator can sign into.
This is sub-change 2/4 of roadmap step ①; grounded in
`docs/organizer-platform-design.md` and `docs/zitadel-tenancy-model.md`,
tracked by liverty-music/specification#759. The organizer-facing API server
and the console frontend are separate sub-changes (3/4, 4/4).

## What Changes

- Introduce the **Organizer** entity (`OrganizerId` UUIDv7, `OrganizerName`),
  distinct from Artist/Performer. It exists only via admin creation →
  existence is the vetting (no `verified` flag). It carries an internal
  `zitadel_org_id` (the tenant org link, backend-only) and an operational
  `provisioning_state` (`provisioning`/`active`/`deactivated`).
- Add the **Organizer↔Artist association**: an Organizer represents many
  Artists, and **each Artist is represented by at most one Organizer**
  (partial-unique on `artist_id`, excluding deactivated organizers so
  their artists are re-associable).
- Add an **admin `OrganizerService`** (bare-verb `Create`, `AssociateArtist`,
  `DisassociateArtist`, `List`, `Get`) behind the existing admin-role gate.
  `Create` takes an `operator_email`; `AssociateArtist` rejects `NOT_FOUND`
  for unknown artists (no create-on-demand) and `ALREADY_EXISTS` for
  already-claimed artists; reassignment = disassociate + associate.
- Add **runtime tenant provisioning**: on `Create`, the backend calls the
  Zitadel Management API (via the `organizer-provisioner` machine user) to
  create the Organizer's tenant org, set its **passkey-primary** login policy
  (mandatory recovery + workspace-IdP federation; NOT passkey-only, NOT
  domain-discovery), Project-Grant `organizer-console`, and seed the initial
  operator as `owner` — **idempotent/compensating** so a retry never
  duplicates the org and never leaves the operator without a grant.
- Add the **operator first-sign-in bootstrap**: the initial operator is a
  tenant human user with no password; Zitadel delivers a passkey-registration
  init link; the operator registers a **passkey** and signs into their org
  (org resolved by **org-pinned entry** — init link / remembered `org_id` /
  org code / "email me a link" → the Zitadel `org:id` scope — not email
  domain).
- Add a **`deactivated` off-switch hook**: the backend rejects all organizer
  operations for a deactivated Organizer and its operators are deactivated
  in Zitadel; freed artists become re-associable. Full teardown cascade is
  Phase 2.
- Emit backend **analytics events** `organizer.created` and
  `organizer.artist.associated`.

Explicit non-goals: the organizer-facing `OrganizerService.Get` + its
dedicated `api.organizer.*` server + org-scoped authz (`organizer-rpc-server`,
4/4); `organizer.html` + hosting (`organizer-console`, 3/4); sub-owner roles;
organizer-side Update/List; full offboarding cascade; slug/contact fields.

## Capabilities

### New Capabilities
- `organizer-accounts`: the Organizer entity + Organizer↔Artist association,
  the admin `OrganizerService`, runtime tenant provisioning + operator
  bootstrap, the `deactivated` hook, and organizer lifecycle analytics.

### Modified Capabilities
<!-- None. Topology was relaxed in organizer-tenancy; this change consumes
     that foundation without further requirement changes to it. -->

## Impact

- **specification**: new `entity/v1/organizer.proto` (Organizer, OrganizerId,
  OrganizerName; protovalidate: id uuid, name 1–200) and
  `rpc/admin/v1/organizer_service.proto` (admin service). Ships via the
  cross-repo release order (spec merge → Release → BSR gen).
- **backend**: Organizer entity + repository + usecases; admin handler behind
  `RequireRoleInterceptor(admin)`; the Zitadel Management-API provisioning
  client (using the `organizer-provisioner` credential); `organizers` +
  `organizer_artists` Atlas migration (partial-unique on `artist_id`,
  `zitadel_org_id` unique, `provisioning_state`); analytics emission.
- **frontend**: admin console gains an organizer-management screen (create /
  associate / disassociate / list) reusing the existing artist search.
- **cloud-provisioning**: none new (the project/role/apps/machine user were
  provisioned in `organizer-tenancy`).
