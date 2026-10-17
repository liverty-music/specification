# Tasks

## 1. specification - main specs, proto comments, docs and the check (one PR)

- [ ] 1.1 Move the operation specs and the story with `git mv`, retitled with the new operation names, in one commit whose message carries the mapping table of proposal "What Changes" (design D1, D3):
  - `entity/organizer/ensure-tenant-org` → `entity/organization/create`, rewritten to its new promise: it creates the Organization named by the short name, and fails with AlreadyExists, with a new scenario "Name already used", when an Organization with that name exists (design D1);
  - `find-tenant-org` → `entity/organization/get-by-name`;
  - `provision-tenant` → `entity/organization/provision`;
  - `deactivate-operators` → `entity/organization/deactivate-identities`;
  - `delete-tenant` → `entity/organization/delete`;
  - `stories/bootstrap-operator-credentials-on-first-sign-in` → `stories/bootstrap-owner-credentials-on-first-sign-in`.

  Verify `openspec validate --specs` and `python3 scripts/check-spec-layout.py` pass.
- [ ] 1.2 In the same commit, reword every main spec under `openspec/specs/` by the vocabulary of design D2: Organizer, member, owner, Organization, identity, admin. This covers requirement and scenario titles and every reference to the moved operations: `usecase/organizer/{create,reconcile-provisioning,deactivate,delete,resolve-caller}`, the stories, `hosted-login`, and the organizer adapters and routes.
  - Review each line with a lowercase "organizer" (`grep -rnE "\borganizers?\b" openspec/specs`, about 90 lines). One that means a person becomes "member" (or "owner" where the text is about the owner role). One that means the business becomes "Organizer". The audience name (paths, `rpc.organizer`, "organizer console") stays.
  - Write the create-or-reuse retry into `usecase/organizer/create` and `usecase/organizer/reconcile-provisioning`: `Organization.Create`; on AlreadyExists, `Organization.GetByName`, whose NotFound fails with Internal; then `Organizer.SetProviderOrganizerID`. Add the scenario "Organization created but not recorded" to `reconcile-provisioning` (design D1).
  - Keep every other requirement's meaning.
  - Record every renamed requirement and scenario title (old → new) and the lowercase-"organizer" decisions in the PR description, because the code repositories' `@spec` annotations follow it.

  Verify `openspec validate --specs` passes, `python3 scripts/check-forbidden-words.py` (task 1.6) passes, and every remaining `\borganizers?\b` hit is the audience name or the business
- [ ] 1.3 In the same commit, reword the deltas of the in-flight changes by design D2, keeping their MODIFIED headers unchanged:
  - `carry-locale-across-auth-boundaries` (`infrastructure/organizer/web/global/i18n`);
  - `verify-attached-media` (`usecase/series/set-cover-image`);
  - `organizer-antisocial-vetting` (`usecase/organizer/deactivate`, `usecase/organizer/record-antisocial-check`).

  Before editing, check with `git -C <store> status --short openspec/changes/<each>/specs` that the store's working tree holds no uncommitted edits to those files; if it does, carry them into the worktree first. Verify `openspec validate <each> --strict` passes and that `grep -rniE "tenant|operator"` over their `specs/` finds nothing
- [ ] 1.4 Reword the comments of the 13 proto files by design D2, including a lowercase "organizer" meaning a person, with no change to any name, number or option. Verify `buf lint`, `buf format -d --exit-code` and `buf breaking --against '.git#branch=origin/main'` pass, and that `grep -rniE "tenant|operator|seller|buyer|applicant" proto` finds only the three `reserved` lines
- [ ] 1.5 Reword `docs/organizer-platform-design.md`, `docs/zitadel-tenancy-model.md`, `docs/ticketing-platform-roadmap.md`, `docs/market-design-notes.md`, `docs/analytics/event-catalog.md` (and `docs/ticketing-platform-roadmap.md:62`, schema.org's `seller`, by naming only the properties the project uses), and `openspec/schemas/liverty-clean-arch/schema.yaml:122` ("token validity, Organization, user"). Archived change ids such as `organizer-tenancy` and the file name `zitadel-tenancy-model.md` stay, because "tenancy" is not forbidden. Verify `grep -rniE "tenant|operator|seller|buyer|applicant" docs openspec/schemas` finds nothing
- [ ] 1.6 Add `scripts/check-forbidden-words.py` (design D4: `tenant`, `operator`, `seller`, `buyer`, `applicant`; the one exception is a proto `reserved` line) and wire it:
  - a `forbidden-words` job in `.github/workflows/buf-pr-checks.yml`, listed in the `needs` of `CI Success`;
  - a `check-forbidden-words` hook in `.pre-commit-config.yaml`;
  - a `words` target in `Makefile`, added to `check`.

  Verify the script exits 0 on the branch and exits 1, printing `path:line` and the replacement hint, on a scratch copy with `operator` added to one spec, `ProvisionTenant` to one proto comment and `buyer_id` to a proto field. Verify it passes on `reserved "buyer_id";`. Then verify `make check` passes
- [ ] 1.7 Write the vocabulary into the repository's ubiquitous-language guidance and verify the three texts agree:
  - `.claude/skills/rpc-design/SKILL.md` "Vocabulary traps": "Organizer" is the business in any letter case; a person using the organizer console is a member; owner is a member's role; their account is an identity in the Organizer's Organization; Liverty Music staff are admins; "tenant", "operator", "seller", "buyer" and "applicant" are not entities, and `scripts/check-forbidden-words.py` rejects them;
  - one review-criteria line in `AGENTS.md`;
  - the same line in the `agent-rules` copy in `CLAUDE.md`.
- [ ] 1.8 Open the PR from a worktree cut from origin/main, staging only the paths of 1.1-1.7. Its description carries the mapping table and the renamed titles of 1.2. Verify `CI Success` (including `forbidden-words`) and `OpenSpec Checks` pass and the PR merges

## 2. backend - the Organization repository (one PR, after 1.8)

Backend identifiers, comments, log fields and test names use the vocabulary of design D2, as proto and the specs do: Organization, member, owner, identity, admin. A lowercase "organizer" meaning a person becomes member. Only the external contracts of design D5 keep the old words.

- [ ] 2.1 Replace `usecase.OrganizerProvisioner` with `entity.OrganizationRepository` in `internal/entity/organization.go`, with the methods `Create`, `GetByName`, `Provision`, `DeactivateIdentities` and `Delete` and their error docs (design D1; `Create` documents AlreadyExists). Move the `.mockery.yml` entry to the entity package and regenerate the mock (`entity/mocks/mock_OrganizationRepository.go`); delete `internal/usecase/organizer_provisioner.go` and `internal/usecase/mocks/mock_OrganizerProvisioner.go`. Verify `make lint` passes
- [ ] 2.2 Rename the implementations to `zitadel.OrganizationRepository`, `NoopOrganizationRepository` and `UnavailableOrganizationRepository` (files `organization_repository{,_noop,_unavailable}.go` and their tests).
  - `EnsureTenantOrg` becomes `Create`: the identity provider's create only, returning AlreadyExists (`apperr`) instead of searching by name.
  - Rename the private helpers and locals named after a tenant or an operator (`ensureOperatorUser` → `ensureOwnerIdentity`, `tenantOrgID`, `operatorID`, `tenantUsers` and the like), the log messages ("tenant org created" → "organization created") and the comments.

  Verify the tests pass under their new names: `TestOrganizationRepository_Provision`, `_Create` (with `@spec components/entity/organization/create "Name already used"` for the AlreadyExists case), `_GetByName`, `_DeactivateIdentities`, `_Delete` and the `_unavailable` tests
- [ ] 2.3 Update `OrganizerUseCase` (`organizer_uc.go`: field, constructor parameter and calls) and `di/provider.go`. Move the create-or-reuse retry into the shared provisioning step of `Create` and `ReconcileProvisioning`: `Organization.Create`; on AlreadyExists, `Organization.GetByName`, whose NotFound becomes Internal; then `Organizer.SetProviderOrganizerID`. Rename the test helpers in `organizer_uc_test.go` (`expectTenantOrg`, `noTenant`, `tenantErr`, `errTenant` and the like). Verify `make test` passes with:
  - the scenarios of `usecase/organizer/{create,reconcile-provisioning,deactivate,delete,resolve-caller}` under their new titles;
  - a new test marked `@spec components/usecase/organizer/reconcile-provisioning "Organization created but not recorded"`;
  - a test for the GetByName-NotFound branch.
- [ ] 2.4 Reword the comments and identifiers across `internal/` and `pkg/config` that use the words for the Organizer's Organization, a member or the owner, an identity, or an admin, and the comments that use a lowercase "organizer" for a person ("organizer operators pick" → "members pick"), by design D2, keeping the kept names of design D5. Verify `git grep -niE "tenant|operator" -- internal pkg cmd` lists only the Pocket Sign `TenantID` / `X-Tenant-ID` / `POCKET_SIGN_TENANT_ID` lines, `LogKeyNeedsOperator` and its message and test, `operator_intervention`, and the External Secrets Operator / NACK comments
- [ ] 2.5 Regenerate `internal/infrastructure/database/rdb/schema/schema.sql` comments by design D2: the `organizers.provider_organizer_id` and `uq_organizers_provider_organizer_id` comments, the `series_images.organizer_id` comment, the `suppressed_concerts` comments ("an admin deleted"), `ticket_sales.name` ("fans and Organizers see"), and the Pocket Sign person-key comments. Add the comment-only Atlas migration for them (db-migration-workflow skill). Verify the migration lint and the migration test pass on a fresh database
- [ ] 2.6 Update every `@spec` annotation to the moved paths and renamed titles of task 1.2. Among them:
  - `components/entity/organization/provision` "Organizer is provisioned", "Repeated call", "Owner email of a fan account", "Retry after a partial failure", "Email rejected by the sign-in service";
  - `components/entity/organization/create` "First attempt" (the old "Earlier attempt created the tenant" scenario moves to `reconcile-provisioning`, task 2.3);
  - `components/entity/organization/get-by-name` (both scenarios);
  - `components/entity/organization/delete` (both scenarios);
  - the organizer adapter scenarios of `artist`, `organizer`, `scanner`, `series`, `series-image`, `ticket-sale`, `ticket-type` and `payout-account`;
  - `hosted-login`, `stories/sign-in-as-organizer`, `usecase/venue/search` and `usecase/organizer/*`.

  Verify `git grep -nE "@spec" | grep -iE "tenant|operator"` finds nothing, and that every `@spec` path in the diff exists under `openspec/specs/` with the quoted scenario title
- [ ] 2.7 Open the PR citing `OpenSpec-Change: rename-organization-operations`; verify `CI Success` passes and the PR merges

## 3. frontend - organizer console names (one PR, after 1.8)

Frontend identifiers, comments, test titles and story names use the vocabulary of design D2, as proto and the specs do. An `operator` meaning a console person becomes member, or owner where the code is about the owner role (the role guard in `roles.ts` and `auth-hook.ts`). `tenant` becomes Organization. A lowercase "organizer" meaning a person becomes member. Only the external contracts of design D5 keep the old words.

- [ ] 3.1 Rename the tenant- and operator-named identifiers and comments in `organizer/`, `admin/` and `shared/config/app-config.ts` by design D2:
  - `roles.ts`: `tenantOrgId` / `tenantDomain` in the claim shape doc; "whether the member holds the `owner` role";
  - `org-enforcement.ts` ("the intended Organization");
  - `auth-hook.ts`, services and UI comments ("the member picks", "the member changes the time").

  Keep the kept names of design D5. Check UI copy in `src/locales` for a person called operator or organizer, and expect none. Verify `make check` passes
- [ ] 3.2 Rename the tests' tenant- and operator-named fixtures and titles (`tenantA`, `tenant-org-a`, the `org-pinned-signin`, `auth-hook` and `roles` specs) and the Storybook stories `OperatorRetries` and `OperatorChangesTheirMind` to their scenarios' new titles (`MemberRetries`, `MemberChangesTheirMind`, or as merged in 1.8). Verify the unit tests and the storybook tests pass, and regenerate the visual baselines only if a story's rendered output changed (it should not)
- [ ] 3.3 Update every `@spec` annotation to the renamed titles of task 1.2. Among them:
  - `stories/sign-in-as-organizer`: "Member signs in and is routed to their Organization by org-pinned entry", "One OIDC client serves all Organizations", "Invited owner lands on the console after accepting the invite", "A reused or mismatched session does not silently onboard the wrong member";
  - `hosted-login`, "Organization is resolved by org-pinned entry for every member";
  - `i18n`, "Member switches to English" and "Member abroad";
  - `action-feedback`, "Member changes their mind";
  - `snack-bar`, "Member retries".

  Use the titles exactly as merged in 1.8. Verify `git grep -nE "@spec" | grep -iE "tenant|operator"` finds nothing, and that every `@spec` path in the diff exists under `openspec/specs/` with the quoted title
- [ ] 3.4 Open the PR citing `OpenSpec-Change: rename-organization-operations`; verify `CI Success` passes and the PR merges

## 4. cloud-provisioning - comments (one PR, any time after 1.8)

- [ ] 4.1 Reword the comments in `src/zitadel/**` and `src/index.ts` that mean the Organizer's Organization, its members or the owner (design D2: "the owner, a member role" rather than "the principal operator"), leaving every resource argument unchanged, including the `organizer-provisioner` machine user's `description` (design D5). Verify `make lint` passes and the diff touches only comment lines (`git diff -U0 | grep -E '^[+-][^+-]' | grep -vE '^\s*[+-]\s*(//|\*|/\*)'` is empty)
- [ ] 4.2 Open the PR citing `OpenSpec-Change: rename-organization-operations`; verify CI passes and the PR merges

## 5. Production check

- [ ] 5.1 After the backend release reaches production, check read-only that the Atlas migration of 2.5 applied (`AtlasMigration` status Ready), the admin console's Organizers list loads, and the admin API logs show no provisioning or reconciler errors for 30 minutes after the rollout
