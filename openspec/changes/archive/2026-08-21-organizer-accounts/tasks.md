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
- [x] 6.3 Verify in prod: an admin creates an Organizer (name + operator email) → tenant org + project grant + `owner` operator provisioned; the operator completes the passkey init link + passkey and signs into their org (org-pinned); associate/disassociate + deactivate behave per spec; analytics events land
  - Provisioning + associate/disassociate + deactivate + analytics: VERIFIED in prod (admin-console-api logs + JetStream `ORGANIZER` stream delivery confirmed).
  - Email delivery: RESOLVED. The passkey-registration mail is delivered end-to-end (confirmed via Postmark + Gmail receipt). Two prod-Zitadel root causes were fixed: (a) SMTP re-activation (`fix-prod-zitadel-instance-config`), and (b) a notification deadlock — `GetNotifyUserByID(shouldTriggered=true)` → `triggerUserProjections … WithAwaitRunning` hit the in-process projection-trigger deadlock (zitadel#10103), so the legacy synchronous notification handler never sent. Fixed by switching Zitadel to parallel notification mode (`Notifications.LegacyEnabled=false`, cloud-provisioning #437), whose River worker path passes `shouldTriggered=false` and avoids the trigger.
  - Passkey-only onboarding: the operator is created via the v2 User API (`AddHumanUser` hardcodes `allowInitMail=false`) so NO password-init mail is sent — only the passkey-registration link, matching the org's passkey-primary policy (backend #398, v1.37.0).
  - Operator passkey onboarding + org-pinned sign-in — **identity layer VERIFIED** at eventstore/projection (does not require the operator's browser): `passwordless.token.added` with a valid `rpID=auth.liverty-music.app` (so zitadel#12191 rpID-missing does NOT apply — the passkey is authenticatable); `user_grants5` roles=`{owner}` on the `organizer-console` project, state active, `resource_owner`=tenant org (org-pinned authorization); tenant-org `login_policies5` `passwordless_type=ALLOWED` + `allow_username_password=false` (passkey-primary, password disabled); operator `resource_owner`=tenant org (org-pinned membership). The passkey therefore authenticates the operator org-pinned with `owner`.
  - **End-to-end operator sign-in UX is DEFERRED to `organizer-console`** (by design). The operator's sign-in destination — `organizer.liverty-music.app`, org-pinned OIDC entry + route guard + post-login welcome — is that separate, not-yet-built change (roadmap step 3/4). `organizer-accounts` delivers only the identity provisioning; there is intentionally no operator-facing app to land in yet. `organizer-console` must issue the passkey/sign-in link **with an OIDC `requestId`** so post-setup redirects into the console (not a bare `CreatePasskeyRegistrationLink` that dead-ends).
  - **Known upstream login-UX constraint** (tracked, not blocking): the hosted `zitadel-login` passkey/set page (v4.14.0) consumes the single-use init code on the first successful ceremony and 500s on any retry — zitadel#12499 (registration code consumed on first click; unfixed) + zitadel#12558 (business errors mis-mapped to HTTP 500; open) + the registration-side analogue of zitadel#12509. Registration SUCCEEDS when the first WebAuthn ceremony completes cleanly; the error only appears on re-submit. We posted our reproduction + eventstore evidence to zitadel#12499. Upgrade `zitadel-login` once those fixes release; `organizer-console`'s `requestId`+redirect design also sidesteps the bare-link dead-end.
