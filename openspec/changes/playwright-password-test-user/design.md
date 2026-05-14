## Context

The dev self-hosted Zitadel instance (cutover landed 2026-04-30 via `self-hosted-zitadel`) currently hosts a single passkey-only test user. Passkey authentication requires a biometric or PIN gesture supplied by the test device — the OS authenticator dialog cannot be driven by headless Playwright, and on WSL2 + WSLg the headed-Chromium fallback (`capture-auth-state.ts`) cannot reliably render the OS-level passkey UI either (the existing `e2e-auth-testing` spec assumes a working display; that assumption is silently violated on WSL2).

Concretely, three things are blocked today:

1. The committed Playwright `.auth/storageState.json` was captured against the pre-cutover Zitadel Cloud issuer and is stale — every `npx playwright test` run fails before reaching application code.
2. The existing capture script (headed Chromium) cannot regenerate the storage state on the developer's WSL2 host.
3. Even on a working display, the passkey credential can't be replayed by Playwright headless because the gesture requirement bypasses any scripted automation.

This change unblocks Playwright by adding a second test user — password-based — that satisfies the headless-capture contract while leaving the existing passkey user in place for device-bound manual testing.

Stakeholders: frontend (E2E pipeline owner), cloud-provisioning (Pulumi-provisions the test user), the developer on WSL2 (primary user of the local capture flow). The change is dev-only; staging and prod test-user provisioning use their own strategies and are out of scope.

## Goals / Non-Goals

**Goals:**

- A password-based `zitadel.HumanUser` exists in the dev self-hosted Zitadel instance, provisioned by Pulumi, separate from the existing passkey user.
- The Playwright `.auth/storageState.json` is regeneratable on WSL2 against the new self-hosted issuer using a headless capture flow (Playwright MCP or equivalent).
- `npx playwright test` runs to completion against the new issuer and exercises the OIDC callback, hydration, and `pre-access-token` webhook integration end-to-end.
- The capture credentials live in a gitignored file under `frontend/.auth/`, consistent with the existing `[reference_e2e_auth]` convention.

**Non-Goals:**

- Replacing or removing the existing passkey test user — passkey remains the canonical UX path for manual smoke testing.
- CI integration of Playwright MCP — the change ships the local capture workflow first; CI automation (GitHub Actions runners regenerating storage state on schedule, or fetching pre-baked state from a private bucket) is deferred to a future change if/when local-only becomes a bottleneck.
- Staging / prod Zitadel test user provisioning — different security posture; separate change.
- Migrating the existing passkey flow off `capture-auth-state.ts` — kept for hosts where headed Chromium works and for device-bound testing.
- Productionizing a 2-factor flow on the password user (TOTP / SMS / etc.) — the user is a single-factor password account, dev only.

## Decisions

### D1: Password-based HumanUser over passkey emulation or WebAuthn-virtual-authenticator

**Choice**: Provision a separate `zitadel.HumanUser` with `InitialPassword` set, alongside the existing passkey user. Both coexist.

**Alternatives considered**:

- **Chrome DevTools virtual authenticator** (`webAuthn.addVirtualAuthenticator`): Playwright can register a virtual platform authenticator and respond to WebAuthn challenges programmatically. Rejected — Zitadel's passkey enrollment binds the credential to the original device's registered authenticator. Replicating that binding in a virtual authenticator requires per-test-run enrollment, which couples capture flow to a live Zitadel admin API call and inverts the "storage state is captured once" contract.
- **Disable passkey enforcement on the test user**: Make the existing user accept both passkey and password. Rejected — Zitadel `LoginPolicy.PasswordlessType=NOT_ALLOWED` cannot be set per-user; it's an org-level toggle, and toggling it taints all sign-ups, not just E2E.
- **Skip Zitadel for E2E**: Mock the OIDC layer for tests. Rejected — would invalidate the whole purpose of the post-cutover regression coverage (we specifically want to exercise the new issuer + `pre-access-token` webhook path).

**Rationale**: A second user is the smallest blast radius. It changes nothing about the passkey user, costs one row in `zitadel-users` table, and is purely additive in the Pulumi diff.

### D2: Playwright MCP headless over patching `capture-auth-state.ts`

**Choice**: New headless capture path using Playwright MCP (no display server needed). Existing `capture-auth-state.ts` (headed Chromium) is retained for the passkey flow on hosts where it works.

**Alternatives considered**:

- **Patch `capture-auth-state.ts` to run headless against the password user**: Possible, but `capture-auth-state.ts` waits for an OS authenticator dialog (passkey gesture) that doesn't exist in the password flow. Rewriting it to handle both modes interleaves two unrelated state machines. Cleaner to ship a second script tailored to password capture.
- **xvfb-run headed-Chromium on WSL2**: Use a virtual framebuffer to give `capture-auth-state.ts` a display. Rejected — already attempted during the cutover; the Chromium window opens but the page stays at `about:blank` past the 5-minute timeout. The bug appears to be in WSLg or Chromium-on-WSL, not fixable in our script.
- **Run Playwright in headed mode on a non-WSL host**: Workable but creates a host-machine dependency for what should be a workstation-portable script.

**Rationale**: Playwright MCP runs Chromium with no display server, sidesteps the WSL2 + WSLg rendering bug, and the dependency is already in the project's evaluation pool (the AGENTS memory references Playwright MCP as a tool the agent has access to). The two scripts targeting two user types keeps each code path single-purpose.

### D3: Credentials in gitignored `.auth/password.md`, NOT GSM

**Choice**: The test user's password lives in `frontend/.auth/password.md` (gitignored, per the existing `[reference_e2e_auth]` convention). Pulumi sets it as the `InitialPassword` and surfaces it via a Pulumi stack output read once at provisioning time.

**Alternatives considered**:

- **GCP Secret Manager**: Mount the password into the frontend container via ExternalSecret. Rejected — the test user is dev-only and read by a local script; pulling it through GSM + ESO adds infrastructure surface for a value that never leaves a developer workstation. GSM is for runtime secrets consumed by deployed workloads.
- **In-cluster K8s Secret only**: Same problem in reverse — the developer needs the password locally for `npx playwright test`, so the K8s-only path doesn't help.
- **Plaintext committed to git**: Rejected, obviously — even for a dev throwaway, a committed credential creates secret-scanning noise and a bad pattern.

**Rationale**: The existing `.auth/` convention already handles a sensitive `password.md` (gitignored) per `[reference_e2e_auth]`. Reusing it is zero new infrastructure.

### D4: Single-factor password (no TOTP) on the test user

**Choice**: The dev test user has password authentication only. No second factor configured.

**Alternatives considered**:

- **Password + TOTP**: Adds realism but requires Playwright to compute TOTP codes at capture time (workable via `otpauth`) and exposes the TOTP seed alongside the password. Rejected — the realism doesn't buy us coverage that mocking the user couldn't, and increases the per-capture-run failure surface.

**Rationale**: Zitadel's default Self-Registration flow already mandates email OTP on first sign-up, which we accept (per the §18.4 decision in the `self-hosted-zitadel` change). For a Pulumi-provisioned user, we skip Self-Registration and arrive directly authenticated, so no email-OTP step is hit. Adding a separate TOTP just to "be realistic" makes the test fragile without protecting anything.

### D5: New `e2e-auth-testing` requirement, not a `MODIFIED` of existing ones

**Choice**: Add a new requirement "Password-Based Test User Capture Path" under `## ADDED Requirements`. Do not MODIFY the existing "StorageState Capture Script" requirement.

**Alternatives considered**:

- **MODIFIED existing "StorageState Capture Script"**: The existing requirement says "execute a setup script ... perform the OIDC login flow with a configured test user". The wording is already user-type-agnostic — no behavior change. Adding a new requirement is more conservative.

**Rationale**: The existing capture-script requirement still describes the passkey flow accurately. We're adding a parallel path, not replacing one.

## Risks / Trade-offs

| Risk | Mitigation |
|---|---|
| Test user becomes a security liability if accidentally enabled in staging / prod. | Pulumi resource is gated to the dev stack (`pulumi.getStack() === "dev"`). Stack-config check in the Pulumi component fails the deploy if the test-user resource is enabled in any non-dev stack. |
| Storage state expires (Zitadel access tokens have a finite TTL); E2E starts failing silently with 401. | Capture script always overwrites with fresh storage state; CI hook (future) detects 401 in the first navigation and re-runs the capture. For now, developer regenerates on demand — documented in `.auth/README.md`. |
| Playwright MCP has its own WSL2 issues we haven't hit yet. | Validate on the developer's actual WSL2 host before declaring §14 done. If MCP fails on WSL2, fall back option is `xvfb-run` + Chromium CDP headless — a smaller intervention than fixing WSLg. |
| Password discoverability — anyone with repo + `.auth/` access can authenticate as the test user. | The user has zero application data (fresh provisioning), no admin role, and exists only on the dev Zitadel instance. Equivalent to any dev-only seed credential. |
| Pulumi `InitialPassword` rotates on resource replace, breaking storage state without warning. | Use Pulumi `ignoreChanges` on the `initialPassword` field after first creation. Document that intentional rotation requires `pulumi up --replace` AND `.auth/password.md` regeneration AND `.auth/storageState.json` regeneration, in that order. |
| Test user shows up in admin console alongside real signups — operator confusion. | Pulumi-managed user has a recognizable display name (`e2e-test-password`) and email domain (`e2e-test@dev.liverty-music.app` or similar). Document the convention in `.auth/README.md`. |

## Migration Plan

This is dev-only and additive; no migration of existing data.

**Rollout order:**

1. `cloud-provisioning`: add the Pulumi `zitadel.HumanUser` resource + initial password Pulumi config; apply to dev stack.
2. Developer pulls the password from the Pulumi output, writes `frontend/.auth/password.md` (gitignored).
3. `frontend`: add the new headless capture script (Playwright MCP path); regenerate `.auth/storageState.json`; commit the storage state file.
4. Run `npx playwright test` locally; verify the full E2E suite passes against the new issuer.
5. Archive the change once all `tasks.md` items are checked off.

**Rollback:** revert the Pulumi commit; Zitadel deletes the test user. Revert the frontend commit; storage state and capture script disappear. The passkey user and its storage state are untouched throughout.

## Open Questions

- Does Playwright MCP support `--storage-state` output mode the same way Playwright CDP does? Need to verify before §3 (capture-script task). If not, fall back: use Playwright MCP to authenticate, dump cookies + localStorage from page context, hand-write the storage-state JSON shape. Tracked in tasks as a §3.x validation step.
- Is the existing `capture-auth-state.ts` worth keeping for the passkey flow given no one currently uses it successfully? Defer the decision: keep until the next person actually needs passkey testing on a host that works.
