# Zitadel Tenancy & RBAC Model

Durable reference for how Liverty Music maps its actors onto Zitadel
resources. Encoded normatively in the `identity-management` capability
spec; this document holds the rationale and the layout so it is
discoverable when reading the specs. Grounded in Zitadel's official B2B
guidance (see References).

## The rule in one line

> **Org = tenant. Project = actor + its RBAC. App = a frontend (auth).**

- **Organization = a tenant.** Zitadel defines an Organization as "a tenant
  in a SaaS system". Each external tenant (Organizer, later Venue) gets its
  own Organization; internal operators stay in the `admin` org; fans stay
  in the `liverty-music` org.
- **Project = one actor's back-office + its RBAC.** Roles, User Grants, and
  Project Grants are all **project-scoped**, so each distinct actor console
  is its own Project, **named by actor** (`organizer-console`, later
  `venue-console`), never a generic `console`. Every mature platform splits
  back-office by actor (Shopify: merchant/POS/partner/org; Ticketmaster:
  promoter/venue/box-office/fan) — a single `console` always has to be
  split later.
- **App = a frontend/entry.** OIDC client config (client_id, redirect URIs,
  token settings) is **per-app**, so a Project can hold several apps sharing
  its role space — e.g. the `organizer-console` web app and a lightweight
  `reception` check-in PWA both live in the `organizer-console` project and
  use its roles.

## Resource layout

```
Zitadel Instance
├── Org: admin  (IaC, isDefault, protect)      internal operators — Google Workspace login
│     └── Project: admin-console               internal vetting / moderation (existing)
├── Org: liverty-music  (IaC)                   fans + product surfaces
│     ├── Project: liverty-music               consumer SPA (existing)
│     └── Project: organizer-console  ★ new     organizer back-office
│           ├── App(OIDC): organizer-console    web console
│           ├── App(PWA):  reception            check-in (later, ⑥) — same roles
│           ├── App(API):  backend-api          audience
│           └── Roles: master [→ editor, viewer, reception (Phase 2)]
│     └── (future) Project: venue-console        venue seat maps / calendar / door lists
├── Org: organizer-<A>  (runtime)  ── ProjectGrant(organizer-console, roles⊆) + UserGrant(staff→master)
├── Org: organizer-<B>  (runtime)  ── ProjectGrant(organizer-console, roles⊆) + UserGrant(staff→viewer)
└── … one org per vetted Organizer
```

Why the `organizer-console` project is **owned by the `liverty-music` org**
(not a new `platform` org, not the `admin` org): the organizer console is a
Liverty-Music product surface, so it belongs with the other product
projects; a separate project (not the fan `liverty-music` project) keeps its
roles, Project Grants, and branding independent; and the `admin` org is
hardened as internal-only (Google Workspace, default org) so an
external-facing app should not live there. The owning org is just the
project's administrative home — Organizer operators authenticate in **their
own** org, so the owning org's login policy never applies to them.

## RBAC flow (how a request is authorized)

1. Admin vets Organizer A → runtime provisioning (below) creates Org A, a
   Project Grant of `organizer-console` (role subset), and a User Grant
   (`master`) for the first operator.
2. Operator signs into the `organizer-console` OIDC app with the org-scope
   `urn:zitadel:iam:org:id:<A>` (pins login to their org).
3. Token carries roles as a nested map
   `urn:zitadel:iam:org:project:{projectId}:roles` =
   `role → { orgId → primaryDomain }`. **The inner orgId is the tenant
   (Organizer) id.** The `aud` includes the backend project id (request the
   `...:project:id:{projectId}:aud` scope).
4. Backend (Go) validates issuer/signature + asserts its project id is in
   `aud`, then reads `{tenant, role}` from the roles claim and authorizes
   the RPC — rejecting any request whose target Organizer the caller has no
   role for. Zitadel holds identity + tenant + role; **which artists/events
   an Organizer may touch is Liverty's own data** (`organizer_artists`,
   event ownership), enforced in the backend.
5. (Optional) A stable business `organizer-id` (Liverty's own PK) can be
   stamped into the token via org metadata + an Action, if keying off the
   Zitadel org id is undesirable.

## Provisioning: IaC vs runtime

| Layer | Managed by | Resources |
|-------|-----------|-----------|
| **Static platform** | IaC (Pulumi) | `admin` + `liverty-music` orgs; the `organizer-console` project, its roles, its apps; the machine user with org-creation rights |
| **Per-tenant (dynamic)** | Runtime — Zitadel **Management API** | one Organizer org + Project Grant + initial User Grant, created **when an admin vets an Organizer** (from the admin console → backend, using the machine-user credential) |

Per-Organizer Terraform would be overkill; tenant orgs are created in the
approval flow via the Management API (Zitadel offers a single
"setup organization" call that creates the org + initial admin). The
backend writes the Organizer row in Postgres in the same operation.

## Caveats

- Many orgs is a supported Zitadel shape (no hard cap); at high density
  enable Instance/Organization caching to avoid an N-over-N read cost.
- The backend MUST validate `aud` **and** authorize off the tenant-scoped
  roles map — never trust a flat role list.
- Custom claims (the optional stable `organizer-id`) require an Action
  (v1 Complement-Token or v2 execution target).

## References (Zitadel official, 2026-08)

- B2B multi-tenant scenario — https://zitadel.com/docs/guides/solution-scenarios/b2b
- Onboard B2B customers using organizations — https://zitadel.com/docs/guides/integrate/onboarding/b2b
- Granted projects (Project Grant) — https://zitadel.com/docs/concepts/structure/granted_projects
- Retrieve user roles (role claim shape) — https://zitadel.com/docs/guides/integrate/retrieve-user-roles
- Reserved scopes (aud / org-id / roles) — https://zitadel.com/docs/apis/openidoauth/scopes
- Actions / custom claims — https://zitadel.com/docs/apis/actions/complement-token
- Terraform provider — https://zitadel.com/docs/guides/manage/terraform-provider
