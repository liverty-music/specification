## Context

See proposal.md, "Why". These facts were checked at origin/main on 2026-10-17.

- **specification**: `tenant` or `operator` occurs in 58 main specs, 13 proto files (all in comments; no message, field or RPC name uses them), 5 docs and one line of the spec schema (`openspec/schemas/liverty-clean-arch/schema.yaml:122`, "token validity, tenant, user"). The words mean four things:
  - the Organizer's Organization ("sign-in tenant", "tenant org");
  - the person using the organizer console ("operator"). The console admits only identities that hold the `owner` role (frontend `organizer/hooks/auth-hook.ts:33`, `organizer/hooks/roles.ts:20`), and main specs call that person "the owner" in some places (`the owner creates`) and a lowercase "organizer" in about 90 lines (`stories/publish-an-organizer-concert`: "an organizer creates, edits and publishes"). Invited members with other roles are planned (liverty-music/specification#1159);
  - Liverty Music staff: the admin console (`infrastructure/admin/web/route/approved-concerts`) and on-call ("reports it as needing an operator", `usecase/order/issue-due-checkouts`, `usecase/checkout/release-expired`);
  - other parties: whoever deploys the fan app (`infrastructure/fan/web/global/app-shell:106`), venue staff (`docs/market-design-notes.md:37`), Pocket Sign's "tenant-scoped" person key (`entity/v1/identity_verification.proto:91-94`), and Zitadel's own definition of an organization as "a tenant in a SaaS system" (`docs/zitadel-tenancy-model.md:13`).
- **No forbidden-word check exists yet.** `unify-ticket-sales` checked its renames with one-off greps in its tasks (`archive/2026-10-12-unify-ticket-sales/tasks.md`, 1.6, 11.1, 11.2) and added no script or workflow. The only required status check on `specification/main` is `CI Success`, from `.github/workflows/buf-pr-checks.yml` (live branch protection, read 2026-10-17; cloud-provisioning `src/index.ts:436`). `openspec-checks.yml` runs only when `openspec/**` changes and is not required.
- **backend**: `usecase.OrganizerProvisioner` (`internal/usecase/organizer_provisioner.go:15-65`) declares `EnsureTenantOrg`, `FindTenantOrg`, `ProvisionTenant`, `DeactivateOperators` and `DeleteTenant`. Its comment says it lives in the usecase layer, "unlike `entity.EmailVerifier`". The project context binds an entity operation to "an interface method declared in backend/internal/entity" (`openspec/config.yaml`). It is implemented by `zitadel.OrganizerProvisioner`, `NoopOrganizerProvisioner` and `UnavailableOrganizerProvisioner` (`internal/infrastructure/zitadel/organizer_provisioner{,_noop,_unavailable}.go`), and mocked from `.mockery.yml:85`. The words also appear with other meanings that are external contracts: Pocket Sign's `X-Tenant-ID` header and `POCKET_SIGN_TENANT_ID` (`internal/infrastructure/pocketsign/verify_client.go:106-154`, `pkg/config/config.go:1074-1123`), the log message `checkout needs an operator`, which a Cloud Monitoring alert matches (`internal/usecase/order_issue_uc.go:41`; cloud-provisioning `src/gcp/components/monitoring.ts:269`), PostgreSQL's `operator_intervention` class (`internal/infrastructure/database/rdb/errors.go:71-73`), Kubernetes operators (Atlas Operator, External Secrets Operator, NACK), and applied migrations (`operator_email`).
- **frontend**: tenant- and operator-named identifiers, comments and test names in `organizer/` and `test/organizer/`, two Storybook stories (`OperatorRetries`, `OperatorChangesTheirMind`), 15 `@spec` annotations quoting renamed scenarios, and no UI copy that uses either word for an Organizer. The fan privacy policy's "business operator" (`src/locales/en/translation.json:597-601`) translates 個人情報取扱事業者, the service's legal operator. Babel plugin names appear in `package-lock.json`.
- **cloud-provisioning**: only comments use the words for the Organizer's Organization or people (`src/zitadel/**`, `src/index.ts:564-574`). The `organizer-provisioner` machine user's `description` (`src/zitadel/components/organizer-provisioner.ts:94-98`) is a live Zitadel resource argument.
- **backend `@spec` annotations** quoting renamed paths or scenarios: 40 lines (for example `internal/infrastructure/zitadel/organizer_provisioner_test.go:286-871`, `internal/usecase/organizer_uc_test.go:556-1231`).

## Goals / Non-Goals

**Goals:**

- One vocabulary everywhere: the entities defined in `components/entity/` and their proto messages are the names the specs, docs, backend and frontend use (owner, 2026-10-17: "proto で entity 定義したユビキタス言語を全てのアプリケーションで一貫して使うべき"). The check keeps the spec repository clean.
- The backend's operation methods match the operation specs, on an interface in `internal/entity` as the project context requires.

**Non-Goals:**

- Inviting members with roles other than `owner` (liverty-music/specification#1159). This change only defines "member" and "owner".
- Renaming `provider organizer ID` / `provider_organizer_id` (the Organizer's link to its Organization). It follows the `provider_<concept>_id` rule (`.claude/skills/rpc-design/SKILL.md`, "Identifiers") and is none of the words.
- Renaming the audience `organizer`: spec paths, `rpc.organizer.v1`, the "organizer console" and the `organizer` host keep it.
- External contracts in code (D5).
- Historical records: `openspec/changes/archive/`, `openspec/migration/`, applied migrations, and archived change ids such as `organizer-tenancy` ("tenancy" is not a forbidden word).

## Decisions

### D1 - The operations become Organization operations; the retry moves to the usecases

| old operation | new operation | promise |
|---|---|---|
| `Organizer.EnsureTenantOrg(short name)` | `Organization.Create(short name)` | creates the Organization named by the short name and returns it; fails with AlreadyExists when an Organization with that name exists, and with Internal otherwise |
| `Organizer.FindTenantOrg(short name)` | `Organization.GetByName(short name)` | returns the Organization with that name, ignoring removed ones; NotFound when none; a read by a natural key, like `Organizer.GetByProviderOrganizerID` |
| `Organizer.ProvisionTenant(id, short name, owner email)` | `Organization.Provision(id, short name, owner email)` | unchanged; a domain verb (rpc-design table), since "set up the sign-in policy, the console grant and the owner identity" has no standard verb |
| `Organizer.DeactivateOperators(id)` | `Organization.DeactivateIdentities(id)` | unchanged: deactivates the members' identities (removes those never signed in), keeps the Organization |
| `Organizer.DeleteTenant(id)` | `Organization.Delete(id)` | unchanged; the resource's own delete |

**The create-or-reuse retry moves to the usecases** (owner decision 2026-10-17). Today `EnsureTenantOrg` calls the identity provider's create and, on AlreadyExists, searches by name (`backend internal/infrastructure/zitadel/organizer_provisioner.go:160-195`). These are two calls with no atomicity between them, unlike `LotteryEntry.GetOrCreateDraft`'s single conditional statement. Deciding to reuse an existing Organization is a retry policy, so it belongs in the usecase. `usecase/organizer/create` and `usecase/organizer/reconcile-provisioning` say, in the direct edit of task 1.2:

1. create the Organization through `Organization.Create`;
2. on AlreadyExists - an earlier attempt created it but did not record it - resolve it through `Organization.GetByName`, where NotFound fails with Internal and leaves the Organizer provisioning for the next run;
3. record it through `Organizer.SetProviderOrganizerID`.

Short names are unique among Organizers, and `admin` and `liverty-music` are reserved, so an Organization with the short name can only be this Organizer's. `reconcile-provisioning` gains the scenario "Organization created but not recorded", and `Organization.Create` gets the scenario "Name already used". Backend tests cover both (tasks 2.2, 2.3). The archive coverage gate does not see direct edits, so those tasks are the only check.

Backend: one interface, `entity.OrganizationRepository` in `internal/entity/organization.go`, replaces `usecase.OrganizerProvisioner`. The entity spec says the identity provider is the only record of an Organization (`components/entity/organization`, Purpose), so it is a repository. Its implementations become `zitadel.OrganizationRepository`, `zitadel.NoopOrganizationRepository` and `zitadel.UnavailableOrganizationRepository` (files `organization_repository{,_noop,_unavailable}.go`). `.mockery.yml` moves the entry from the usecase package to the entity package (`entity/mocks/mock_OrganizationRepository.go`). The usecase field becomes `organizationRepo`.

- **Why move the interface now**: the project context binds operations to `internal/entity`. The interface's own comment records the deviation, and the schema makes moving it "a change of its own" (`schema.yaml:102-105`). Every line that names it changes here anyway.
- **Rejected - `Organization.GetOrCreate`** (first draft of this plan): it hides a non-atomic retry inside an operation (owner).
- **Rejected - leaving the operations under `entity/organizer`**: they act on the Organization, by its id or name, and change nothing on the Organizer. The issue also asks for the move.

### D2 - The vocabulary

Defined in the entity Purposes, edited directly in this PR:

- `components/entity/organizer`: "The people who run it are its members: a member is a person with an identity in the Organizer's Organization ... Every member holds a role; owner is the only role today";
- `components/entity/organization`: an Organizer's Organization holds "the identities of that Organizer's members".

| meaning | old | new |
|---|---|---|
| the business | Organizer, organizer (lowercase, meaning the business) | Organizer |
| a person who uses the organizer console for an Organizer | operator, initial operator, organizer operator, a lowercase organizer meaning a person ("the organizer publishes it") | a member (of the Organizer); the owner where the text is about the owner role or the owner identity specifically |
| the member's account at the identity provider | operator (as an account), operator user | an identity in the Organizer's Organization; the owner identity |
| the Organizer's sign-in unit | tenant, tenant org, sign-in tenant, Zitadel tenant | the Organizer's Organization (an Organization in general statements) |
| several of them | tenants, per-tenant, multi-tenant, org-per-tenant | Organizations, per Organizer, one Organization per Organizer |
| Liverty Music staff | operator (admin console, on-call, operator-initiated) | an admin, admin-initiated |
| whoever deploys an app | the operator | the deployer, or a passive sentence |
| venue staff | operator-tablet | staff tablet |
| a provider's account scope | Pocket Sign tenant-scoped | scoped to Liverty Music's account at the verification provider |
| the console guard's phrasing | the caller's tenant | the caller's Organization |
| a party in a sale (docs) | seller, buyer, applicant | the Organizer, the User, the fan who entered |

"Organizer" means the business wherever it appears; no rule depends on letter case. The audience name `organizer` is a name, not a person: "organizer console" reads as the Organizer's console. Requirement and scenario titles change with their text, for example "Operator completes first login by enrolling a passkey" → "Owner completes first login by enrolling a passkey", "Operator retries" → "Member retries", and "Tenant with no Organizer" → "Organization with no Organizer". Each implementing repository updates its `@spec` annotations to the new titles (tasks 2.6, 3.3).

- **Why "member" plus the role "owner"**: a person and their role are different things. Invited members with other roles come with #1159, and "member" keeps every sentence true then. Where a sentence is about the role (the invitation, the owner identity, the console's role guard), it says owner.
- **Why no exceptions for other meanings**: rephrasing a dozen sentences costs less than an allowlist, which would need maintaining and would let the Organizer meaning back in through an allowed line.
- **Lowercase "organizer" for a person** is not machine-checkable: the audience name and "Organizer" in any case stay legal. Task 1.2 reviews each of the about 90 lines and records the decisions in the PR description.

### D3 - Moves and wording are made directly on the main specs, not through deltas

The five operation specs and the story are moved with `git mv`, retitled, and reworded in the same commit as the vocabulary edits on the other main specs. The PR description carries the mapping table.

- **Why**: the schema says moving main specs is not a change and is done directly in one commit with a mapping table (`schema.yaml:309-311`). `unify-ticket-sales` moved and renamed operation specs this way (tasks 1.6 and 11.1). No requirement's meaning changes (the one rule that moves, the create-or-reuse retry, keeps its observable result; D1), and deltas would need a full MODIFIED copy of the 110 requirements that contain the words.
- **Why not ADDED at the new path plus REMOVED at the old one**: the old specs and every requirement a MODIFIED block names would keep the words on main until archive. The check could then cover `openspec/specs/` only after archive, and would need either an exclusion list in the meantime or a second step to widen its scope.
- **Cost**: from the spec PR until the backend PR, the main specs name `Organization.Provision` and the usecase-side retry while the code says `ProvisionTenant` and `EnsureTenantOrg`, and the backend's `@spec` annotations point at the old paths. The window is closed by group 2, and tasks 2.6 and 3.3 verify that no annotation names an old path or title. The archive coverage gate does not apply (no ADDED or MODIFIED scenarios), so those tasks are the only check.
- In-flight deltas are reworded in the same commit (proposal, "Capabilities"). `carry-locale-across-auth-boundaries` MODIFIES the i18n requirement "Japanese or English, chosen on the device"; its scenarios "Operator switches to English" and others would come back with the whole block at archive.

### D4 - The forbidden-word check

- **Script**: `scripts/check-forbidden-words.py` (Python 3 standard library, like `check-spec-layout.py`). It reads the files git tracks under `proto/`, `docs/`, `openspec/specs/` and `openspec/schemas/` and matches `tenant`, `operator`, `seller`, `buyer` and `applicant` case-insensitively, inside words too (`ProvisionTenant`, `DeactivateOperators`, `operator_email`, `multi-tenant`, `buyer_id`). The one exception is a proto line that starts with `reserved`, which keeps a removed field name from being reused: `entity/v1/lottery_entry.proto:125` (`applicant_id`), `order.proto:239` (`buyer_id`) and `organizer.proto:76` (`seller_details`). The script has no other exception. `seller`, `buyer` and `applicant` are the words `unify-ticket-sales` removed (the audit greps in its tasks.md, e.g. task 8.2); today they occur only in those three lines and `docs/ticketing-platform-roadmap.md:62`. `holder` is not checked: as a substring it matches "placeholder". It prints `path:line: <word> - use <replacement>`, with the replacement hints of D2, and exits 1 on any hit. The words and hints are one table at the top of the script, so a later rename adds a row.
- **Scope**:
  - `proto/`, because generated code carries the comments to both clients;
  - `openspec/specs/`, the ubiquitous language;
  - `docs/`;
  - `openspec/schemas/`, because its instructions are pasted into every agent that writes a spec.

  `openspec/changes/` is excluded: proposals, designs and REMOVED or Migration text name old names on purpose, and archives are history. `.claude/skills/`, `AGENTS.md`, `CLAUDE.md` and README are excluded because the rule itself names the words there.
- **Wiring**:
  - a job `forbidden-words` in `buf-pr-checks.yml`, added to the `needs` of `CI Success`, the one required check. It runs on every PR without a path filter, because it reads the whole tree in about a second and fails on violations already on main as well as new ones;
  - a `pre-commit` hook with `files: ^(proto|docs|openspec/(specs|schemas))/`;
  - a `words` target in `Makefile`, added to `check`. Cloud threads run `make check` and no hooks (CLAUDE.md, workflow).
- **Rejected - a step in `openspec-checks.yml`**: it runs only when `openspec/**` changes and is not required, so a proto- or docs-only PR would skip it.
- **Rejected - one-off greps in tasks, as `unify-ticket-sales` did**: they do not stop the words from coming back, which the issue asks for.

### D5 - No forbidden-word check in backend, frontend or cloud-provisioning

The code repositories use the same vocabulary as the specs and proto (Goals; D2). Identifiers, comments, test names and story names that mean the Organizer's Organization, a member, the owner, an identity or an admin are renamed to those words, and so is a lowercase "organizer" meaning a person. They keep the other meanings, which are external contracts:

- backend keeps Pocket Sign's `TenantID` and `X-Tenant-ID`, `POCKET_SIGN_TENANT_ID`, `LogKeyNeedsOperator` and its message, `operator_intervention`, the Kubernetes operator names and applied migrations;
- frontend keeps the privacy policy's legal term and the Babel plugin names;
- cloud-provisioning keeps `atlas-operator`, External Secrets Operator, the `checkout-needs-operator` alert and runbook, and the machine user `description`.

A word check there would need an allowlist longer than the rule (owner decision 2026-10-17: no check in those repositories). The source names come from specs and proto, which the check covers, and code review enforces the entity vocabulary (CLAUDE.md, "Review criteria").

- **Why the log message stays** (owner agreed 2026-10-17): renaming it means the alert must match both messages across a deploy (`unify-ticket-sales` task 11.3 did this for `reservation` → `checkout`). It names on-call work, not an Organizer, and no reader is misled by it. The specs that describe it say "needing an admin" and do not quote the message.
- **Why the machine user description stays**: changing it updates a live Zitadel resource on the next `pulumi up`, for a text nobody reads.

### D6 - Order

The specification PR goes first (group 1): main specs, proto comments, docs, the check, the skill and the rules. Proto edits are comments, so no Release is needed for the code PRs; the next Release carries them. Backend (group 2), frontend (group 3) and cloud-provisioning (group 4) are independent of each other and of BSR.

## Risks / Trade-offs

- [The specs name methods the backend does not have yet, and annotations dangle] → D3 cost; tasks 2.6 and 3.3 verify the annotations; group 2 lands right after group 1.
- [An in-flight change archives with the old words] → its archive PR fails `CI Success` with the word and its replacement; the same commit rewords the deltas known today (D3).
- [The check flags a legitimate future use, such as quoting a provider's API] → rephrase it, or add a row to the script's table with an explicit exemption in the same PR, which a reviewer sees.
- [The backend migration that changes only comments still runs in production at merge] → `COMMENT ON` takes a brief lock and is reversible; it is in the Atlas migration flow like any other.
- [A lowercase "organizer" meaning a person survives, since the check cannot tell it from the audience name] → task 1.2 reviews every hit and lists the decisions; code review keeps it out later.
- [The retry moves from one method to two usecase steps, and a mistake re-creates an Organization] → `Organization.Create` fails with AlreadyExists rather than creating a second one, so a wrong retry fails loudly; the usecase tests of tasks 2.2-2.3 cover the AlreadyExists and NotFound branches.

## Migration Plan

1. specification PR (group 1); verify `CI Success` passes, including the new job.
2. backend, frontend and cloud-provisioning PRs, in any order. Each is a rename with unchanged tests, except the backend's moved retry (D1), which gets its own tests. The backend migration changes comments only.
3. Production read-only check after the backend deploy (task 5.1): the admin console lists Organizers and the reconciler logs no provisioning errors.
4. Rollback: revert the PR. No data or identity-provider state changes.

## Open Questions

- None.
