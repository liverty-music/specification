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
status)` + `organizer_artists(organizer_id, artist_id)` with a
**partial UNIQUE(artist_id) WHERE status != 'deactivated'** so a
deactivated Organizer frees its artists. Both FKs `ON DELETE CASCADE`.
`zitadel_org_id` is the token-tenant→Organizer link (DB is source of truth;
backend-only, not on the consumer proto). `status` is an
operational lifecycle flag (`provisioning`/`active`/`deactivated`) — NOT the
business `verified` flag the design rejected. `*_at` names per schema-lint.

**D2 — Proto.** `entity/v1/organizer.proto` (Organizer, OrganizerId=uuid,
OrganizerName min_len=1/max_len=200, matching the `ArtistName` convention).
The admin service is `rpc/admin/organizer/v1/organizer_service.proto`, package
`liverty_music.rpc.admin.organizer.v1`, with **bare-verb** methods `Create`,
`AssociateArtist`, `DisassociateArtist`, `List`, `Get`, `ListArtists`, and
`Deactivate` (the last is the admin-surface trigger for the D6 off-switch — the
earlier 5-method list under-enumerated it). Each RPC documents its error matrix
(INVALID_ARGUMENT / NOT_FOUND / ALREADY_EXISTS / PERMISSION_DENIED). `Create`/
`Get` return the `Organizer` entity and `List` returns `repeated Organizer` —
**no response-DTO wrapper and no status enum** (existence is the vetting; the
operational lifecycle stays a backend-only `status` column). The artists an
Organizer represents are returned by `ListArtists(organizer_id)`, kept in this
organizer package rather than bundled into the organizer responses or added to
the consumer `rpc.artist.v1` ArtistService (resource-oriented; no organizer
coupling leaks into the consumer API).

**Package convention.** Services are laid out uniformly as
`liverty_music.rpc.<audience>.<domain>.v1` (audience ∈ consumer/admin/organizer;
one service per package → **bare message names**, no `OrganizerService`-prefix).
Services are never shared across packages; only the higher-privilege **admin**
server may additionally mount consumer/organizer handlers as needed (a
server-wiring concern, not a package one). The organizer-facing `Get` is a
separate service under `rpc.organizer.organizer.v1`, defined and served in
`organizer-rpc-server` (4/4), not here. Migrating the existing
`rpc.admin.v1.ConcertService` and the consumer `rpc.<domain>.v1` packages onto
this convention is **out of scope** for this change.

**D3 — Admin-gated only.** All RPCs ride the existing admin Connect server
behind `RequireRoleInterceptor(admin)`. There is no organizer-scoped
authorization in this change (that is the organizer-facing server, 4/4).

**D4 — Provisioning saga (idempotent, compensating), keyed on OrganizerId.**
Order: (1) insert `organizers` row `status=provisioning`; (2)
Management API create tenant org (name `org-<full-uuid>` — the full OrganizerId,
NOT a short prefix: the first 8 hex of a UUIDv7 are its millisecond timestamp, so
a prefix collides for any two organizers created within the same ~65s window,
which would resolve the second into the first's tenant [cross-tenant `owner`
grant]; explicit
**passkey-primary** login policy per `organizer-tenancy`:
`passwordlessType=ALLOWED`, `allowUsernamePassword=false`,
`allowRegister=false`, `allowExternalIDP=true`, `ignoreUnknownUsernames=true`;
NOT domain-discovery); (3) persist `zitadel_org_id`; (4) Project-Grant
`organizer-console` (role subset incl. `owner`); (5) create operator human
user (no password, `request_passwordless_registration` → passkey init link) +
`owner` User Grant; (6) compare-and-set `status` `provisioning`→`active` (a
conditional update, NOT an unconditional set: a concurrent `Deactivate` during
the multi-second saga must not be clobbered by a trailing activation — a
superseded CAS is a no-op and deactivation wins). A reconciler re-enters
at the first incomplete step (each Zitadel create existence-checked). Uses the
`organizer-provisioner` credential from ESC/Secret Manager (JWT-profile →
short-lived tokens). Wrap the call in an OTel span + an
`organizer_provisioning_failed` metric.

*Provisioner hardening (carried over from the `organizer-tenancy` code-review,
recorded in its design "deferred" list):* isolate GCP-layer read access to the
provisioner key with a **dedicated `admin-console-api` workload + GCP SA** (so the
`backend-app` SA no longer reads the `IAM_ORG_MANAGER` key — an IaC /
cloud-provisioning change alongside this backend work), and make the provisioner
key **immutable (far-future expiry)** rather than finite-expiry + manual rotation:
Zitadel machine keys have no native rotation, so a finite expiry is a silent
day-N outage; the long-lived key is instead contained by the GSA isolation +
short-lived operational tokens + instant force-replace revocation (this
**supersedes** the earlier key-expiry-alert plan).

*Isolated-workload data access (gap found in prod — the isolated workload runs
the same backend binary and must reach Postgres):* the `admin-console-api` GSA
needs its **own** Cloud SQL identity, not `backend-app`'s. It connects via the
in-process Cloud SQL Go connector under Workload Identity, so grant it BOTH
`roles/cloudsql.client` (`instances.connect`) **and** `roles/cloudsql.instanceUser`
(`instances.get`/login), create a dedicated `CLOUD_IAM_SERVICE_ACCOUNT` Postgres
user (`admin-console-api@<project>.iam`), override `DATABASE_USER` on the
Deployment to that user (an explicit container `env` wins over the shared
`server-config` `envFrom`), and grant that IAM user `app`-schema privileges via a
migration. Cloud SQL IAM auth ties the DB user to the connecting GSA, so the
isolated workload cannot reuse `backend-app`'s DB user; without this it
CrashLoopBackOffs. (Shipped as cloud-provisioning #405/#406 + backend #390.)

**D5 — Operator bootstrap.** The operator is created without a password;
Zitadel delivers a **passkey-registration init link** so they register a
passkey on first sign-in. The tenant org's login policy (set in step 2) is
**passkey-primary** with a mandatory recovery path (admin re-invite via
re-issued init link; optional step-up magic-link/OTP) and permits workspace-IdP
federation. **Org resolution is org-pinned** (org-scoped init link → remembered
`org_id` → org code / "email me a link" → the `org:id` scope), NOT email-domain
discovery — so no per-tenant domain verification and gmail operators work. (The
console URL/config carrier is `organizer-console`.)

**D6 — Deactivation hook.** `status=deactivated` gates the
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
- **`status` looks like reversing "no status column"** → it is an
  *operational* lifecycle flag, explicitly distinct from the rejected
  business `verified` flag; called out so review does not read it as a
  reversal.
- **Analytics events without a fan UserId** → model as admin-actor / group
  events keyed on `organizer_id`; confirm they are forwarded despite lacking
  a person `distinct_id`.

## Migration Plan

1. specification: additive proto → merge → Release → BSR gen.
2. backend: Atlas migration (`organizers` + `organizer_artists`, partial
   unique, `zitadel_org_id`, `status`); entity/repo/usecases;
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
