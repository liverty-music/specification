## Why

`reuse-fan-email-for-organizer-sign-in` introduced the entity Organization (the identity provider's sign-in unit, one per Organizer) and the Organizer's owner email. It left the old words on everything else (its design.md Non-Goals; liverty-music/specification#1158). The Organizer's operations are still named after a "tenant" (`EnsureTenantOrg`, `FindTenantOrg`, `ProvisionTenant`, `DeleteTenant`) and an "operator" (`DeactivateOperators`). Main specs, proto comments, docs and Go code still use the words for three different things: the Organizer's Organization, the person using the organizer console, and Liverty Music's own admins. No entity defines either word, which breaks the review rule that names come from `components/entity/` (`CLAUDE.md`, "Review criteria"). Nothing stops the words from coming back.

## What Changes

- **The five identity-provider operations move from the Organizer to the Organization and get Organization names**:

  | old | new |
  |---|---|
  | `components/entity/organizer/ensure-tenant-org` (`Organizer.EnsureTenantOrg`) | `components/entity/organization/get-or-create` (`Organization.GetOrCreate`) |
  | `components/entity/organizer/find-tenant-org` (`Organizer.FindTenantOrg`) | `components/entity/organization/get-by-name` (`Organization.GetByName`) |
  | `components/entity/organizer/provision-tenant` (`Organizer.ProvisionTenant`) | `components/entity/organization/provision` (`Organization.Provision`) |
  | `components/entity/organizer/deactivate-operators` (`Organizer.DeactivateOperators`) | `components/entity/organization/deactivate-identities` (`Organization.DeactivateIdentities`) |
  | `components/entity/organizer/delete-tenant` (`Organizer.DeleteTenant`) | `components/entity/organization/delete` (`Organization.Delete`) |

  Their promises do not change. The story `stories/bootstrap-operator-credentials-on-first-sign-in` becomes `stories/bootstrap-owner-credentials-on-first-sign-in`.
- **One word for each meaning, everywhere in proto, specs, docs and the spec schema**:
  - a tenant, a tenant org or a sign-in tenant → the Organizer's **Organization**;
  - a person using the organizer console → the **owner**, the only role the console admits today;
  - an operator as an account at the identity provider → an **identity** of the Organizer's Organization;
  - an operator as Liverty Music staff (admin console, on-call) → an **admin**.

  Words with any other meaning (a deployer, venue staff, a provider's "tenant") are rephrased too, so the check needs no exceptions. Requirement and scenario titles that contain the words are renamed. Behavior does not change.
- **Go and TypeScript names follow.** In the backend, the usecase-layer `OrganizerProvisioner` port becomes `entity.OrganizationRepository` with the five methods above, its Zitadel, no-op and unavailable implementations and the mock are renamed, and so are the tenant- and operator-named locals, test names and comments. The frontend renames its tenant- and operator-named identifiers, story names and comments. cloud-provisioning renames comments only. Every `@spec` annotation that quotes a renamed path or scenario is updated.
- **A forbidden-word check**: `scripts/check-forbidden-words.py` rejects `tenant` and `operator` in any letter case, as words or inside identifiers, in `proto/`, `docs/`, `openspec/specs/` and `openspec/schemas/`. It runs in the required `CI Success` gate, as a pre-commit hook and in `make check`.
- No API, data or wire change: proto edits are comments only, and the identity provider's resources keep their names.

## Capabilities

### New Capabilities

None. The five operation specs and the story are moved and renamed directly on the main specs, in one commit with a mapping table (spec schema, "Capability files": moving main specs is not a change). This change carries the implementation that renames the code to match.

### Modified Capabilities

None at requirement level. The wording edits keep every requirement's meaning; they are made directly on the main specs together with the moves (precedent: `unify-ticket-sales` tasks 1.6 and 11.1). `.openspec.yaml` sets `skip_specs: true`.

- `components/entity/organizer` (Purpose): unchanged. Its requirement "Only an active Organizer serves its operators" is renamed to "Only an active Organizer serves its owner" in the same commit.
- `components/entity/organization` (Purpose): unchanged. Its operations are listed in the mapping table above.

In-flight changes whose deltas use the words, and are reworded in the same commit so their archive does not bring them back: `carry-locale-across-auth-boundaries` (`infrastructure/organizer/web/global/i18n`), `verify-attached-media` (`usecase/series/set-cover-image`) and `organizer-antisocial-vetting` (`usecase/organizer/deactivate`, `usecase/organizer/record-antisocial-check`). `admin-organizer-status-and-delete` (#1164, being planned) adds `stories/retire-an-organizer` and touches the admin Organizer adapter. Its author was asked to use the new words, and the check rejects them in its archive PR otherwise.

## Impact

- **specification**: 58 main specs (wording; 5 operation specs and 1 story moved), 13 proto files (comments only, no release needed), 5 docs, the spec schema (one word), the `rpc-design` skill (a vocabulary trap), `AGENTS.md` and `CLAUDE.md` (a review-criteria line), the new script, `.github/workflows/buf-pr-checks.yml`, `.pre-commit-config.yaml` and `Makefile`.
- **backend**: `internal/usecase/organizer_provisioner.go` → `internal/entity/organization.go`; `internal/infrastructure/zitadel/organizer_provisioner*.go` → `organization_repository*.go`; `.mockery.yml` and the regenerated mock; `organizer_uc.go`, `di/provider.go`, the tests and the `@spec` annotations; comments in the DB schema, with one comment-only migration.
- **frontend**: organizer console hooks, services and UI comments; test and story names; `@spec` annotations.
- **cloud-provisioning**: comments in `src/zitadel/` and `src/index.ts`.
- **production**: no data, identity-provider or API change. The backend migration changes only column and index comments.
