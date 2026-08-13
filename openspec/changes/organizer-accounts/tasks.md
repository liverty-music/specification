## 1. Specification (proto)

- [ ] 1.1 `entity/v1/organizer.proto`: `Organizer` (OrganizerId UUIDv7, OrganizerName), type-safe wrappers + protovalidate (id `uuid`, name `min_len=1/max_len=200`)
- [ ] 1.2 `rpc/admin/v1/organizer_service.proto`: bare-verb `Create` (name + operator_email), `AssociateArtist`, `DisassociateArtist`, `List`, `Get`; document each RPC's error matrix
- [ ] 1.3 `buf lint`/`format`/`breaking` pass; open specification PR, merge, cut Release, confirm BSR gen succeeds

## 2. Backend — domain & admin surface

- [ ] 2.1 Atlas migration: `organizers` (id, name, `zitadel_org_id` UNIQUE, `provisioning_state`, `*_at`) + `organizer_artists` (partial UNIQUE(artist_id) WHERE not deactivated; FKs ON DELETE CASCADE)
- [ ] 2.2 `entity` Organizer + repository interface; rdb repo with error classification
- [ ] 2.3 Usecases: create, associate/disassociate artist (NOT_FOUND / ALREADY_EXISTS), list, get, deactivate
- [ ] 2.4 Admin `OrganizerService` handler behind `RequireRoleInterceptor(admin)`

## 3. Backend — tenant provisioning & bootstrap

- [ ] 3.1 Zitadel Management-API client (using the `organizer-provisioner` credential) — create org, set passkey-only + domain-discovery login policy, project-grant `organizer-console`, create operator user + `master` grant
- [ ] 3.2 Idempotent/compensating provisioning saga keyed on OrganizerId (DB-row-first, existence-checked steps, reconciler retry); persist `zitadel_org_id`; flip to `active`
- [ ] 3.3 Operator bootstrap: no-password human user + Zitadel init email (passkey on first sign-in)
- [ ] 3.4 Deactivation: `deactivated` gate rejects organizer ops + deactivates Zitadel operators + frees artists
- [ ] 3.5 OTel span + `organizer_provisioning_failed` metric on the provisioning call

## 4. Backend — analytics & tests

- [ ] 4.1 Emit `organizer.created` + `organizer.artist.associated` (JetStream→PostHog, keyed on organizer_id); add to the event catalog
- [ ] 4.2 Tests: usecases (create/associate/disassociate incl. double-claim + non-existent-artist), provisioning-client mock incl. compensating retry, deactivation gate; `make check` passes with upgraded BSR package

## 5. Frontend (admin console)

- [ ] 5.1 Organizer-management screen: create (name + operator email), list with associated artists, associate/disassociate (reuse existing artist search), deactivate
- [ ] 5.2 `make check` passes with upgraded BSR package

## 6. Release & ship to prod

- [ ] 6.1 Backend PR merged → release → prod pin bump; confirm rollout (depends on `organizer-tenancy` IaC applied in the env first)
- [ ] 6.2 Frontend PR merged → release
- [ ] 6.3 Verify in prod: an admin creates an Organizer (name + operator email) → tenant org + project grant + master operator provisioned; the operator completes init-email + passkey and signs into their org; associate/disassociate + deactivate behave per spec; analytics events land
