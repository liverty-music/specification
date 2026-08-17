## 1. Specification (proto)

- [x] 1.1 `entity/v1/organizer.proto`: `Organizer` (OrganizerId UUIDv7, OrganizerName), type-safe wrappers + protovalidate (id `uuid`, name `min_len=1/max_len=200`)
- [x] 1.2 `rpc/admin/organizer/v1/organizer_service.proto` (package `liverty_music.rpc.admin.organizer.v1`, bare message names): bare-verb `Create` (name + operator_email), `AssociateArtist`, `DisassociateArtist`, `List`, `Get`, `ListArtists`, `Deactivate`; responses return the `Organizer` entity (no view DTO / status enum); `ListArtists` returns the roster; document each RPC's error matrix
- [x] 1.3 `buf lint`/`format`/`breaking` pass; open specification PR, merge, cut Release, confirm BSR gen succeeds

## 2. Backend — domain & admin surface

- [x] 2.1 Atlas migration: `organizers` (id, name, operator_email, `zitadel_org_id` partial-UNIQUE, `status` SMALLINT 1–3) + `organizer_artists` (UNIQUE(artist_id); deactivation/disassociation delete rows to free the artist; FKs ON DELETE CASCADE)
- [x] 2.2 `entity` Organizer + repository interface; rdb repo with error classification
- [x] 2.3 Usecases: create, associate/disassociate artist (NOT_FOUND / ALREADY_EXISTS), list, get, deactivate
- [x] 2.4 Admin `OrganizerService` handler behind `RequireRoleInterceptor(admin)`

## 3. Backend — tenant provisioning & bootstrap

- [x] 3.1 Zitadel Management-API client (using the `organizer-provisioner` credential, JWT-profile → short-lived tokens) — create org, set **passkey-primary** login policy (recovery + `allowExternalIDP` + `ignoreUnknownUsernames`; NOT passkey-only/domain-discovery), project-grant `organizer-console`, create operator user + `owner` grant
- [x] 3.2 Idempotent/compensating provisioning saga keyed on OrganizerId (DB-row-first, existence-checked steps, reconciler retry); persist `zitadel_org_id`; flip to `active`
- [x] 3.3 Operator bootstrap: no-password human user + Zitadel passkey-registration init link (passkey on first sign-in); org resolution is org-pinned (not domain discovery)
- [x] 3.4 Deactivation: `deactivated` gate rejects organizer ops + deactivates Zitadel operators + frees artists
- [x] 3.5 OTel span + `organizer_provisioning_failed` metric on the provisioning call
- [x] 3.6 (hardening, from `organizer-tenancy` code-review) cloud-provisioning: dedicated `admin-console-api` workload + GCP SA to isolate GCP-layer read access to the provisioner key (so `backend-app` SA no longer reads the `IAM_ORG_MANAGER` key); make the provisioner key immutable (far-future, like `backend-app`) rather than finite-expiry + manual rotation — Zitadel machine keys have no native rotation, so the long-lived key is contained by the GSA isolation + short-lived operational tokens + instant force-replace revocation (supersedes the earlier key-expiry-alert plan)
- [x] 3.7 (gap found in prod) admin-console-api Cloud SQL access: the isolated GSA needs its OWN DB identity — grant `roles/cloudsql.client` + `roles/cloudsql.instanceUser`, create a dedicated `CLOUD_IAM_SERVICE_ACCOUNT` Postgres user (`admin-console-api@<project>.iam`), override `DATABASE_USER` on the Deployment (explicit env over shared `server-config` envFrom), and grant `app`-schema privileges via migration (cloud-provisioning #405/#406 + backend #390); without it the workload CrashLoopBackOffs

## 4. Backend — analytics & tests

- [x] 4.1 Emit `organizer.created` + `organizer.artist.associated` (JetStream→PostHog, keyed on organizer_id); add to the event catalog
- [x] 4.2 Tests: usecases (create/associate/disassociate incl. double-claim + non-existent-artist), provisioning-client mock incl. compensating retry, deactivation gate; `make check` passes with upgraded BSR package

## 5. Frontend (admin console)

- [x] 5.1 Organizer-management screen: create (name + operator email), list with associated artists, associate/disassociate (reuse existing artist search), deactivate
- [x] 5.2 `make check` passes with upgraded BSR package

## 6. Release & ship to prod

- [x] 6.1 Backend PR merged → release → prod pin bump; confirm rollout (depends on `organizer-tenancy` IaC applied in the env first)
- [x] 6.2 Frontend PR merged → release
- [ ] 6.3 Verify in prod: an admin creates an Organizer (name + operator email) → tenant org + project grant + `owner` operator provisioned; the operator completes the passkey init link + passkey and signs into their org (org-pinned); associate/disassociate + deactivate behave per spec; analytics events land
  - Provisioning + associate/disassociate + deactivate + analytics: VERIFIED in prod (admin-console-api logs + JetStream `ORGANIZER` stream delivery confirmed).
  - **Blocked**: the operator passkey-link step depends on prod Zitadel actually delivering email. Prod Zitadel currently has no active SMTP provider (0 sends on Postmark; `SendPasswordlessRegistration` is accepted but not delivered), and the bare-login redirect points at the dev console — both are prod Zitadel instance-config issues tracked separately in `fix-prod-zitadel-instance-config` (SMTP `smtp-activation` self-heal + `AdminOrgConfigComponent` `consoleUrl` wiring). Complete 6.3's passkey step after that ships.
