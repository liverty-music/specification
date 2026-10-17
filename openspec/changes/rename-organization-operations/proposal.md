## Why

`reuse-fan-email-for-organizer-sign-in` introduced the entity Organization (the identity provider's sign-in unit, one per Organizer) and the Organizer's owner email. It left the old words on everything else (its design.md Non-Goals; liverty-music/specification#1158). The Organizer's operations are still named after a "tenant" (`EnsureTenantOrg`, `FindTenantOrg`, `ProvisionTenant`, `DeleteTenant`) and an "operator" (`DeactivateOperators`). Main specs, proto comments, docs and code use these words, and a lowercase "organizer", for different things:

- the Organizer's Organization;
- the person using the organizer console;
- Liverty Music's own admins.

No entity defines "tenant", "operator" or a person called "organizer". That breaks the review rule that names come from `components/entity/` (`CLAUDE.md`, "Review criteria"), and nothing stops the words from coming back. The same holds for "seller", "buyer" and "applicant", which `unify-ticket-sales` removed but did not guard.

## What Changes

- **One vocabulary, defined by the entities and used in every repository**:
  - **Organizer** is the business, whatever the letter case;
  - a person who uses the organizer console for an Organizer is a **member** of that Organizer;
  - **owner** is a role a member holds, today the only one;
  - the member's account at the identity provider is an **identity** in the Organizer's **Organization**;
  - Liverty Music staff are **admins**.

  The replacements are: tenant / tenant org → the Organizer's Organization; operator, or a lowercase organizer meaning a person → member (owner where the text is about the owner role); operator meaning an account → identity; operator meaning staff or on-call → admin. The audience name `organizer` stays (spec paths, `rpc.organizer.v1`, "organizer console": the Organizer's console). Words with any other meaning are rephrased. Requirement and scenario titles that contain the words are renamed. Behavior does not change.
- **The five identity-provider operations move from the Organizer to the Organization**:

  | old | new |
  |---|---|
  | `components/entity/organizer/ensure-tenant-org` (`Organizer.EnsureTenantOrg`) | `components/entity/organization/create` (`Organization.Create`): creates the Organization named by the short name; AlreadyExists when one with that name exists |
  | `components/entity/organizer/find-tenant-org` (`Organizer.FindTenantOrg`) | `components/entity/organization/get-by-name` (`Organization.GetByName`) |
  | `components/entity/organizer/provision-tenant` (`Organizer.ProvisionTenant`) | `components/entity/organization/provision` (`Organization.Provision`) |
  | `components/entity/organizer/deactivate-operators` (`Organizer.DeactivateOperators`) | `components/entity/organization/deactivate-identities` (`Organization.DeactivateIdentities`): deactivates the members' identities |
  | `components/entity/organizer/delete-tenant` (`Organizer.DeleteTenant`) | `components/entity/organization/delete` (`Organization.Delete`) |

  Today `EnsureTenantOrg` creates the Organization or, when an earlier attempt already created it, returns that one. That retry moves to the usecases that provision: `OrganizerUseCase.Create` and `ReconcileProvisioning` call `Organization.Create`, and on AlreadyExists resolve the Organization through `Organization.GetByName`. The observable result is unchanged: a retried provisioning still creates no second Organization. The story `stories/bootstrap-operator-credentials-on-first-sign-in` becomes `stories/bootstrap-owner-credentials-on-first-sign-in`.
- **Backend and frontend identifiers and comments follow the same vocabulary**:
  - In the backend, the usecase-layer `OrganizerProvisioner` port becomes `entity.OrganizationRepository` with the five methods above, and its implementations and mock are renamed. Tenant- and operator-named locals, helpers, test names and comments become Organization, member, owner or identity.
  - The frontend renames its operator- and tenant-named identifiers, story names and comments to member, owner and Organization.
  - cloud-provisioning renames comments only.
  - Every `@spec` annotation that quotes a renamed path or scenario is updated.
- **A forbidden-word check**: `scripts/check-forbidden-words.py` covers `proto/`, `docs/`, `openspec/specs/` and `openspec/schemas/`. It rejects `tenant`, `operator`, `seller`, `buyer` and `applicant` in any letter case, as words or inside identifiers. The one exception is a proto `reserved` line. It runs in the required `CI Success` gate, as a pre-commit hook and in `make check`. The code repositories get no word check.
- No API, data or wire change: proto edits are comments only, and the identity provider's resources keep their names.

## Capabilities

### New Capabilities

None. The five operation specs and the story are moved and renamed directly on the main specs, in one commit with a mapping table (spec schema, "Capability files": moving main specs is not a change; owner decision 2026-10-17). This change carries the implementation that renames the code to match.

### Modified Capabilities

None through deltas; `.openspec.yaml` sets `skip_specs: true`. The wording edits keep every requirement's meaning and are made directly on the main specs together with the moves (precedent: `unify-ticket-sales` tasks 1.6 and 11.1). The one rule that moves between specs is the create-or-reuse retry: it leaves the operation spec for `usecase/organizer/create` and `usecase/organizer/reconcile-provisioning`. It is written there in the same direct edit, with a scenario for an Organization created earlier but never recorded.

- `components/entity/organizer` (Purpose, edited directly in this PR): defines a member ("a person with an identity in the Organizer's Organization") and owner as a member's role.
- `components/entity/organization` (Purpose, edited directly in this PR): an Organizer's Organization holds the identities of that Organizer's members.

In-flight changes whose deltas use the words, reworded in the same commit as the main specs so their archive does not bring the words back:

- `carry-locale-across-auth-boundaries` (`infrastructure/organizer/web/global/i18n`);
- `verify-attached-media` (`usecase/series/set-cover-image`);
- `organizer-antisocial-vetting` (`usecase/organizer/deactivate`, `usecase/organizer/record-antisocial-check`).

`admin-organizer-status-and-delete` (liverty-music/specification#1168) is handled by its own author.

## Impact

- **specification**:
  - 58 main specs, for the words: 5 operation specs and 1 story moved, and `usecase/organizer/{create,reconcile-provisioning}` take the retry;
  - about 90 lines with a lowercase "organizer" that are checked one by one for the person meaning;
  - 13 proto files (comments only; no release needed);
  - 5 docs and the spec schema (one line);
  - the vocabulary in the `rpc-design` skill, `AGENTS.md` and `CLAUDE.md`;
  - the new script, `.github/workflows/buf-pr-checks.yml`, `.pre-commit-config.yaml` and `Makefile`.
- **backend**:
  - `internal/usecase/organizer_provisioner.go` → `internal/entity/organization.go`;
  - `internal/infrastructure/zitadel/organizer_provisioner*.go` → `organization_repository*.go`, with `EnsureTenantOrg` split into `Create` and the existing `GetByName`;
  - the AlreadyExists retry in `organizer_uc.go`;
  - `.mockery.yml` and the regenerated mock, `di/provider.go`, the tests and the `@spec` annotations;
  - DB schema comments, with one comment-only migration.
- **frontend**: organizer console hooks, services, UI comments and identifiers; test and story names; `@spec` annotations.
- **cloud-provisioning**: comments in `src/zitadel/` and `src/index.ts`.
- **production**: no data, identity-provider or API change. The backend migration changes only column and index comments.
