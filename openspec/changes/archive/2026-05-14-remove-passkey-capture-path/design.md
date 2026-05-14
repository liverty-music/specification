## Context

`playwright-password-test-user` (archived 2026-05-14) folded an `Existing Passkey Capture Path Retained` requirement into main `e2e-auth-testing/spec.md`. The Implementation Deltas section of that change's `design.md` already documented why the requirement was operationally vacuous on the active self-hosted dev Zitadel and queued THIS change as the loop-closer.

This is a pure-removal change. There are no new components, no new capabilities, no new infrastructure. The "design" question is therefore not "how do we build something" but "what are the trade-offs in removing it, and what do we explicitly defer".

## Goals / Non-Goals

**Goals:**

- Bring **both** affected capability specs into alignment with reality on self-hosted dev Zitadel. `e2e-auth-testing` retires the `Existing Passkey Capture Path Retained` requirement (the script the requirement names no longer functions). `identity-management` MODIFIES `Provision Password-Based E2E Test User in Dev Zitadel` to drop the "distinct from the existing passkey-only test user" phrasing and REMOVES `Test User Coexists with Passkey User` (the coexistence requirement asserts a user state that does not exist).
- Eliminate dead code (`frontend/scripts/capture-auth-state.ts`) and misleading documentation (`AGENTS.md` + `.auth/README.md` references to a wiped user).
- Leave a clear forward-pointer for any future WebAuthn / passkey CI regression testing need.

**Non-Goals:**

- Re-provisioning a passkey test user on the self-hosted dev Zitadel. The next change that needs passkey coverage should design the approach from scratch (virtual authenticator) rather than restore the deleted lineage.
- Cleaning up the inert `pepperoni9+playwright-1@gmail.com` row in the Zitadel Cloud tenant. Cloud retention is governed by `self-hosted-zitadel §15.1` / `§18.10` (indefinite no-cost rollback escape hatch); the user has no DNS, no OIDC traffic, and no operational impact. A future Cloud-decommission change can fold the cleanup in.
- Touching the password capture path. The `Password-Based Storage State Capture Path`, `Test-User Credential File Gitignored`, and the user-type-agnostic `Playwright MCP Authenticated Session` / `StorageState Capture Script` / `StorageState Gitignore` requirements remain unchanged and continue to describe the live capability correctly.

## Decisions

### D1: REMOVE rather than MODIFY the retired requirement

**Choice**: Treat this as a normative behavioural change (REMOVED in the delta), not a documentation refresh (MODIFIED with caveats).

**Alternatives considered**:

- **MODIFY the requirement** to say "the script is retained for future passkey re-provisioning". Rejected — there is no committed re-provisioning plan, and the spec should not invent one to justify keeping dead code.
- **Leave the spec as-is and only update frontend docs**. Rejected — the spec is the source of truth on the capability; letting it drift from the live code (no script, no user) defeats the point of having one.

**Rationale**: REMOVED with a clear `Reason:` + `Migration:` block is the honest formulation. The capability narrows by one requirement; downstream consumers (developers, agents, future changes) get a clean signal that the path is intentionally gone.

### D2: Do not preempt the future WebAuthn-testing design

**Choice**: Do not author a placeholder `Future Passkey CI Regression Testing` requirement now. The REMOVED block's `Migration:` text points at virtual authenticator as the likely direction if/when the need surfaces — that's the limit of what this change commits to.

**Alternatives considered**:

- **Add an ADDED requirement reserving the design space** ("the system SHOULD support virtual-authenticator-based WebAuthn testing"). Rejected — speculative; commits the project to building something nobody asked for and that would constrain the eventual design.

**Rationale**: Spec hygiene. Don't pollute the capability with placeholders for unrequested work.

### D3: Cloud-tenant user cleanup deferred

**Choice**: Leave the user row on the Zitadel Cloud tenant untouched. Document the deferral in `proposal.md` Out-of-scope and this design.md Goals/Non-Goals.

**Alternatives considered**:

- **Delete the Cloud user as part of this change**. Rejected — the Cloud tenant retention decision is upstream of any single user-cleanup task. If/when an `archive-zitadel-cloud-tenant`-class change reopens, the user-cleanup belongs there. Folding it in here would split the Cloud-tenant retention question across two changes.

**Rationale**: Scope discipline. The user is inert (no DNS, no OIDC traffic, no cost); deferring its cleanup costs nothing.

## Risks / Trade-offs

| Risk | Mitigation |
|---|---|
| A future developer needs to QA the passkey login UX manually and finds the script gone. | The `.auth/README.md` "Historical note" footer points at the deleted script's history + virtual-authenticator as the future direction. Restoring the script from git history is a single `git show <sha>:scripts/capture-auth-state.ts > scripts/capture-auth-state.ts` away if someone really needs the headed flow on a display-capable host. |
| `playwright-password-test-user`'s recently-archived "Existing Passkey Capture Path Retained" requirement is REMOVED only ~hours after it was added. The change history will show the path was retained, then immediately retired. | This is the honest record. The retention was a hedge made during a busier change; the verify pass on that change surfaced the issue (W1) and this change resolves it. The git log narrative ("retained → discovered vacuous → removed") is readable and informative. |
| If the Cloud tenant is ever decommissioned and the `pepperoni9+playwright-1@gmail.com` user along with it, an entry will exist in git history that some future grep may surface confusingly. | The `.auth/README.md` Historical note documents why. Future grep readers will find the explanation in the same paragraph that mentions the user name. |

## Migration Plan

Pure removal — no migration of state or runtime data. Specification PR + frontend PR can land in either order:

1. `specification` PR REMOVES `Existing Passkey Capture Path Retained` from `e2e-auth-testing`, MODIFIES `Provision Password-Based E2E Test User in Dev Zitadel` and REMOVES `Test User Coexists with Passkey User` from `identity-management`, and adds this change's artifacts (`proposal.md`, this `design.md`, `tasks.md`, the two spec deltas under `specs/`).
2. `frontend` PR `git rm`s the script + simplifies the docs.
3. After both merge, `/opsx:archive remove-passkey-capture-path` folds both deltas into main: `e2e-auth-testing/spec.md` loses one requirement; `identity-management/spec.md` updates one requirement in place and loses another.

**Rollback**: revert both PR merges. The spec requirement comes back, the script comes back from git history, the docs revert. The dead path is restored, but functionally nothing changes because the user it targets is still gone — rollback only undoes the cleanup.

## Open Questions

None. The Cloud-tenant cleanup question is closed by D3 (deferred). The future-WebAuthn-testing question is closed by D2 (not preempted). The script-deletion question is closed by D1 (REMOVE, not MODIFY).
