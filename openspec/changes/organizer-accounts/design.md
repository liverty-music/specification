## Context

See proposal.md - Why. Builds on `organizer-tenancy` (the shared
`organizer-console` project, `owner` role, apps, and `organizer-provisioner`
machine user, plus the relaxed topology). Full design, resolved gap-audit,
and the four-change decomposition are in
[`docs/organizer-platform-design.md`](../../../docs/organizer-platform-design.md);
Zitadel mechanics in
[`docs/zitadel-tenancy-model.md`](../../../docs/zitadel-tenancy-model.md).
This design references them rather than restating.

## Goals / Non-Goals

**Goals:** the Organizer entity + association, the admin management surface,
robust runtime tenant provisioning, operator first-sign-in bootstrap, a
minimal off-switch, and lifecycle analytics.

**Non-Goals:** the organizer-facing `Get` + `api.organizer.*` server +
org-scoped authz (`organizer-rpc-server`); `organizer.html` + hosting
(`organizer-console`); sub-owner roles; organizer-side Update/List; full
offboarding cascade; slug / contact fields.

## Decisions

**D1 — Data model.** `organizers(id UUIDv7, name, zitadel_org_id UNIQUE,
provisioning_state)` + `organizer_artists(organizer_id, artist_id)` with a
**partial UNIQUE(artist_id) WHERE provisioning_state != 'deactivated'** so a
deactivated Organizer frees its artists. Both FKs `ON DELETE CASCADE`.
`zitadel_org_id` is the token-tenant→Organizer link (DB is source of truth;
backend-only, not on the consumer proto). `provisioning_state` is an
operational lifecycle flag (`provisioning`/`active`/`deactivated`) — NOT the
business `verified` flag the design rejected. `*_at` names per schema-lint.

**D2 — Proto.** `entity/v1/organizer.proto` (Organizer, OrganizerId=uuid,
OrganizerName min_len=1/max_len=200, matching the `ArtistName` convention);
`rpc/admin/v1/organizer_service.proto` with **bare-verb** methods
`Create`, `AssociateArtist`, `DisassociateArtist`, `List`, `Get`. Each RPC
documents its error matrix (INVALID_ARGUMENT / NOT_FOUND / ALREADY_EXISTS /
PERMISSION_DENIED). The organizer-facing `Get` service is defined and served
in `organizer-rpc-server` (4/4), not here.

**D3 — Admin-gated only.** All RPCs ride the existing admin Connect server
behind `RequireRoleInterceptor(admin)`. There is no organizer-scoped
authorization in this change (that is the organizer-facing server, 4/4).

**D4 — Provisioning saga (idempotent, compensating), keyed on OrganizerId.**
Order: (1) insert `organizers` row `provisioning_state=provisioning`; (2)
Management API create tenant org (name `org-<uuid-short>`, explicit
**passkey-primary** login policy per `organizer-tenancy`:
`passwordlessType=ALLOWED`, `allowUsernamePassword=false`,
`allowRegister=false`, `allowExternalIDP=true`, `ignoreUnknownUsernames=true`;
NOT domain-discovery); (3) persist `zitadel_org_id`; (4) Project-Grant
`organizer-console` (role subset incl. `owner`); (5) create operator human
user (no password, `request_passwordless_registration` → passkey init link) +
`owner` User Grant; (6) set `provisioning_state=active`. A reconciler re-enters
at the first incomplete step (each Zitadel create existence-checked). Uses the
`organizer-provisioner` credential from ESC/Secret Manager (JWT-profile →
short-lived tokens). Wrap the call in an OTel span + an
`organizer_provisioning_failed` metric.

*Provisioner hardening (carried over from the `organizer-tenancy` code-review,
recorded in its design "deferred" list):* isolate GCP-layer read access to the
provisioner key with a **dedicated provisioner workload + GCP SA** (so the
`backend-app` SA no longer reads the `IAM_ORG_MANAGER` key — an IaC /
cloud-provisioning change alongside this backend work), and add a **key-expiry
monitoring alert** for the finite provisioner key (expires 2027-08-13) plus the
rotation runbook.

**D5 — Operator bootstrap.** The operator is created without a password;
Zitadel delivers a **passkey-registration init link** so they register a
passkey on first sign-in. The tenant org's login policy (set in step 2) is
**passkey-primary** with a mandatory recovery path (admin re-invite via
re-issued init link; optional step-up magic-link/OTP) and permits workspace-IdP
federation. **Org resolution is org-pinned** (org-scoped init link → remembered
`org_id` → org code / "email me a link" → the `org:id` scope), NOT email-domain
discovery — so no per-tenant domain verification and gmail operators work. (The
console URL/config carrier is `organizer-console`.)

**D6 — Deactivation hook.** `provisioning_state=deactivated` gates the
backend (reject all organizer ops) and deactivates the Zitadel operators;
the partial-unique index frees the artists. Full teardown (org/grant
removal) is Phase 2 — the hook ships now so it is not a later migration.

**D7 — Analytics.** Emit `organizer.created` / `organizer.artist.associated`
via the existing JetStream→PostHog path, keyed on `organizer_id` (admin-actor
/ group events, no fan UserId); add them to the event catalog in this change.

## Risks / Trade-offs

- **Two-system saga without 2PC** → the DB-row-first + existence-checked,
  reconciler-retried design (D4) makes a partial failure recoverable without
  duplicates; the operator is never left without an `owner` grant.
- **`provisioning_state` looks like reversing "no status column"** → it is an
  *operational* lifecycle flag, explicitly distinct from the rejected
  business `verified` flag; called out so review does not read it as a
  reversal.
- **Analytics events without a fan UserId** → model as admin-actor / group
  events keyed on `organizer_id`; confirm they are forwarded despite lacking
  a person `distinct_id`.

## Migration Plan

1. specification: additive proto → merge → Release → BSR gen.
2. backend: Atlas migration (`organizers` + `organizer_artists`, partial
   unique, `zitadel_org_id`, `provisioning_state`); entity/repo/usecases;
   admin handler; provisioning client + reconciler; analytics; tests
   (incl. the compensating-retry and double-claim paths).
3. frontend: admin console organizer-management screen.
4. cloud-provisioning (hardening, from the `organizer-tenancy` code-review):
   a dedicated provisioner workload + GCP SA for GCP-layer key-access isolation,
   and a key-expiry monitoring alert for the provisioner key.
- Rollback: additive tables + additive proto; remove the screen and tables
  (no tenant orgs exist until Create is used).

## Open Questions

- Whether the initial operator is seeded in the same `Create` call or invited
  immediately after — resolved as **same call** here (so the E2E "an owner
  signs in" is verifiable); revisit only if invite-later UX is needed (Phase
  2), which would not change these specs.
