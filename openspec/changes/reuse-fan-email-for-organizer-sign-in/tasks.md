# Tasks

Every test task cites its scenarios with `@spec <capability-path> "<scenario>"` so `scripts/check-scenario-coverage.py` finds them at archive.

## 0. Live checks on the identity provider

- [x] 0.1 On the existing Organizer's Organization (`org-01a124ae-…`, id 394467236179345732): create an identity with the owner's fan email; verify it is accepted, the user name `<email> (<organizer name>)` is accepted, and email sign-in with a passkey works through the console opened with `?org_id=`
  - Done (2026-10-15): identity 395182603667243270 `pepperoni9@gmail.com (XX Records)` created, invited, granted `owner`, passkey registered; with `ignoreUnknownUsernames` off, typing `pepperoni9@gmail.com` signed in to it (hosted login shows `pepperoni9@gmail.com (XX Records)`); with it on, the passkey step failed ("Could not request passkey challenge"); fan app sign-in with the same email unchanged; `pannpers+org-e2e@pannpers.dev` still signs in; a sign-in naming no organization resolved to the fan account. Along the way: `userLoginMustBeDomain` was set and removed again on this organization only (its users' names were restored); the organization's login policy now has `ignoreUnknownUsernames` off. The console crashed after the callback (`AUR3500`), unrelated.
- [x] 0.2 List every organization in prod Zitadel with its effective domain policy
  - Done (2026-10-15): `admin` (372892288692584603), `liverty-music` (373015514391249051), `org-01a124ae-c0b7-7a11-8bbe-5cfedacd9082` (394467236179345732); all inherit the instance default (`userLoginMustBeDomain`, `validateOrgDomains`, `smtpSenderAddressMatchesInstanceDomain` all false). Org-level domain policies need `iam.policy.write` (`proto/zitadel/admin.proto:2492-2499`); `organizer-provisioner` (`IAM_ORG_MANAGER`) cannot set them. This change sets none.
- [ ] 0.3 Verify `?org=<short name>` (design D4) on the existing Organization after renaming it in 6.1 (or on a throwaway Organization): sign in with the scope `urn:zitadel:iam:org:domain:primary:<short name>.auth.liverty-music.app` and type the email; verify the Organization's policy and branding apply, email sign-in with a passkey succeeds, and the generated primary domain follows the rename; record the result and design D4's choice here
- [x] 0.4 Ask the owner for the existing Organizer's short name and record it here; verify it matches `^[a-z][a-z0-9-]{2,31}$` and is not reserved
  - Done (2026-10-15): `e2e-test` (matches the pattern; not reserved). The owner also kept the send limits (3 per address, 10 per client, per 60 minutes) and chose to delete the verification identity 395182603667243270 in 6.1.

## 1. Proto (specification → BSR)

- [ ] 1.1 `entity/v1/organizer.proto`: `OrganizerShortName` with the protovalidate `pattern: "^[a-z][a-z0-9-]{2,31}$"` and `not_in: ["admin", "liverty-music"]`, `short_name = 10` (OUTPUT_ONLY), entity comment without "tenant" and "operator"; verify `buf lint` and `buf format -d` pass and a protovalidate test rejects `XX Records`, `ab` and `admin`
- [ ] 1.2 `rpc/admin/organizer/v1/organizer_service.proto`: `CreateRequest.operator_email` → `owner_email` (field 2), required `short_name = 3`, comments rewritten; verify `buf lint` passes and `buf breaking` reports only the field rename
- [ ] 1.3 `rpc/organizer/v1/organizer_service.proto`: `SendSignInLinks` with errors InvalidArgument and ResourceExhausted; verify `buf lint` and `buf breaking` (additive) pass
- [ ] 1.4 Open the proto PR from a worktree cut from origin/main with this change's plan, merge with the `buf skip breaking` label for 1.2, cut a Release; verify `buf-release.yml` succeeds and record the BSR Go and npm versions here; close liverty-music/specification#1149 with a link to this change

## 2. Backend — entity and schema

- [ ] 2.1 Atlas migration: `short_name` (CHECK, unique, nullable until 6.1), `operator_email` → `owner_email` with the 165-character CHECK, comments, `schema.sql`; verify `atlas migrate lint`, the drift check and `migration_grants_integration_test.go` pass
- [ ] 2.2 `entity.Organizer`: `ShortName`, `OwnerEmail` and the validation; verify unit tests for `entity/organizer` "Empty name", "Name too long", "Valid short name", "Malformed short name", "Reserved short name", "Malformed owner email", "Owner email too long" pass
- [ ] 2.3 Repository `Create` with the short name; verify contract tests for `entity/organizer/create` "Organizer is stored", "Same name and owner email twice", "Short name already used" pass against the test database

## 3. Backend — provisioning (design D7)

- [ ] 3.1 `EnsureTenantOrg` and `FindTenantOrg` by the short name; verify contract tests for `entity/organizer/ensure-tenant-org` "First attempt", "Earlier attempt created the tenant" and `entity/organizer/find-tenant-org` "Tenant left by a failed attempt", "No tenant" pass against the Zitadel test double
- [ ] 3.2 `ensureHumanUser` with the user name `<owner email> (<short name>)`, org-scoped AlreadyExists handling; `ensureLoginPolicy` with `IgnoreUnknownUsernames: false`, `DisableLoginWithEmail: false`, `HidePasswordReset: true`; remove `CheckOperatorEmailAvailable` and the instance-wide search; verify contract tests for `entity/organizer/provision-tenant` "Organizer is provisioned", "Owner email of a fan account", "Repeated call", "Retry after a partial failure", "Email rejected by the sign-in service" and organizer hosted-login "A provisioned tenant org has the passkey-primary policy" pass
- [ ] 3.3 `OrganizerUseCase.Create` with the short name and without the email check; verify unit tests for `usecase/organizer/create` "Organizer is created", "Same name again", "Short name already used", "Owner email of a fan account", "Owner email rejected during provisioning" and `usecase/organizer/reconcile-provisioning` "Owner email rejected" pass

## 4. Backend — sign-in links and handlers (design D5)

- [ ] 4.1 `Organizer.ListByOwnerEmail`; verify contract tests "Owner of two Organizers", "Deactivated Organizer", "Unknown email" pass
- [ ] 4.2 `Organizer.SendSignInLinks` (Postmark, Japanese, `?org=<short name>` links); verify contract tests "Two Organizers" (recorded request) and "Mail service unavailable" pass
- [ ] 4.3 `OrganizerUseCase.SendSignInLinks` with the per-address limiter and the background send; verify unit tests "Owner asks for links", "Address that owns nothing", "Mail service unavailable", "Fourth request for one address" pass
- [ ] 4.4 Organizer handler `SendSignInLinks`, `auth.OrganizerPublicProcedures()`, the per-client limit; verify handler tests for `adapter/organizer/api/rpc/organizer` "Owner asks for sign-in links", "Unknown address", "Malformed address", "Too many requests", `usecase/organizer/send-sign-in-links` "Eleventh request from one client", and that every other organizer procedure still answers Unauthenticated without a sign-in
- [ ] 4.5 Admin handler with `owner_email`, `short_name` and the short name on reads; `PayoutAccountUseCase.Get` with the owner email; verify handler tests for `adapter/admin/api/rpc/organizer` "Name too long", "Malformed short name", "Malformed owner email", "Missing OrganizerId", "Missing rate", "Admin lists Organizers and inspects a roster", "Admin reads any Organizer", "Admin deletes a deactivated Organizer", "Delete refused", "Admin records business details", "Short name already used" and unit tests for `usecase/payout-account/get` "First call", "Provider unreachable on first call", "Unknown Organizer" pass
- [ ] 4.6 Upgrade the generated package, run `make check`, open the backend PR citing the change and the store commit, merge; verify the production rollout is healthy and the AtlasMigration status is applied

## 5. Frontend (design D4)

- [ ] 5.1 `org-handle.ts`: `org` is a short name and signs in with the primary-domain scope (or the 0.3 fallback); `main.ts`: no Organization → `find-organizer`, never `signIn()`; verify tests for `organizer-shell` "New device", "Remembered Organization" and organizer hosted-login "Device that remembers no Organization", "Owner whose email is also a fan account" pass
- [ ] 5.2 `find-organizer` route; verify tests "Owner asks for the link", "Address that runs nothing", "Malformed address", "Too many requests", "Link opened" pass
- [ ] 5.3 Admin console organizer screen: short name and owner email fields; verify its component test passes
- [ ] 5.4 Run `make check`, open the frontend PR citing the change and the store commit, merge; verify the production rollout is healthy and a fresh browser profile opening `https://organizer.liverty-music.app/` shows the find-organizer screen

## 6. Production

- [ ] 6.1 Existing Organizer (design Migration Plan step 4): set the short name from 0.4 in its row (break-glass SQL per `cloud-provisioning/docs/runbooks/cloud-sql-access.md`), rename its Organization, converge its login policy, rename its identities' user names to `<email> (<short name>)`, delete the 2026-10-15 verification identity 395182603667243270 unless the owner keeps it, then apply the `NOT NULL` migration; verify by reading back the row, the Organization's name and policy and its users
- [ ] 6.2 Verify by hand in prod and record here, marking the story scenarios `@spec-manual` with the date: `stories/sign-in-as-organizer` "Fan becomes an Organizer's owner" (create a test Organizer with the owner's fan email), "Owner on a new phone with the short name", "Owner on a new phone without the short name"; `entity/organization` "Fan email in an Organizer's Organization", "Same email in two Organizers", "Same email twice in one Organization"; fan hosted-login "Fan whose email also runs an Organizer"; then deactivate and delete the test Organizer

## 7. Follow-ups

- [ ] 7.1 File the follow-up issues and record their links here: (a) rename the tenant- and operator-named Organizer operations into `entity/organization` with the forbidden-word CI check; (b) owner-invited team members with roles; (c) per-Organizer SSO routed from the find-organizer screen; (d) the console crashes after the sign-in callback when it lands on `/` (`AUR3500`, `organizer/auth-callback/auth-callback-route.ts`, `organizer/model/concert-model.ts:190`); (e) `SeriesService.SetCoverImage` accepts another Organizer's `series_image_id` (`backend/internal/usecase/series_uc.go:806-820`, `rdb/series_repo.go:161`); (f) the product organization's registration offers password sign-up (`register-form.tsx:160`), contrary to the fan hosted-login spec; verify each link resolves
