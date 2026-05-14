## Context

The archived `playwright-password-test-user` change provisioned a password-based `zitadel.HumanUser` (`e2e-test-password@dev.liverty-music.app`) via Pulumi. During §3.5 live-ops verification on WSL2 + WSLg, the headless capture script hit Zitadel's default "change password on first sign-in" gate: `@pulumiverse/zitadel.HumanUser` v0.2.0 sets the user's credential state with `changeRequired = true` and exposes no provider knob to flip it. The frontend capture script was patched (frontend#353) to detect the `/password/change` redirect and re-submit the current password as the "new" one.

That workaround is the subject of this change. It works today, but is fragile in three ways:

1. **Depends on Zitadel's default password-history policy.** The product org's `PasswordComplexityPolicy` currently has no `historySize` constraint, so `new = current` is accepted. A future Zitadel policy change enabling history checking silently breaks the capture script on its first run thereafter.
2. **Re-submission flow adds two navigations** (POST `/password/change` → GET redirect → eventual OIDC callback). Each is latency and a failure surface.
3. **The contract is hidden in script comments.** A new developer reading `capture-auth-state-password.ts` sees `[4b/5] Clearing first-sign-in password-change prompt…` with no obvious explanation; the rationale lives in a comment block above the handler that is easy to miss.

The proper fix is to drive Zitadel into the desired state at provision time, using the same Pulumi Dynamic Resource pattern the project already employs for `ZitadelSmtpActivation`, `ZitadelTarget`, `ZitadelExecutionFunction`, `ZitadelUserIdpLink` (all under `cloud-provisioning/src/zitadel/dynamic/`). Add one more: `ZitadelHumanUserPasswordPermanent`, which calls Zitadel Management API's `POST /management/v1/users/{user_id}/password` with `noChangeRequired: true` immediately after the HumanUser is created.

Stakeholders: cloud-provisioning (owns the Pulumi composition for the dev Zitadel topology), frontend (owns the E2E capture script that is currently working around the missing flag), the developer running headless Playwright on WSL2 (consumer of the simpler post-fix capture flow).

Scope: dev only. The parent `Zitadel` class is gated to the dev stack already; there is no production `E2eTestUserComponent` to update.

## Goals / Non-Goals

**Goals:**

- A new `ZitadelHumanUserPasswordPermanent` Pulumi Dynamic Resource exists under `cloud-provisioning/src/zitadel/dynamic/permanent-password.ts`, modeled on `smtp-activation.ts`. It calls the Management API to mark a HumanUser's password permanent (`noChangeRequired: true`).
- `E2eTestUserComponent` wires the new resource immediately after the `zitadel.HumanUser` is created. The same ESC-sourced password is fed to both the HumanUser's `initialPassword` AND the new Dynamic Resource — they always agree.
- The `[4b/5]` password-change handler block in `frontend/scripts/capture-auth-state-password.ts` (and its 5-step → 4-step renumbering) is removed. The script becomes simpler: navigate → submit username → submit password → wait for OIDC callback.
- Post-apply, the dev `e2e-test-password` user signs in directly without a `/password/change` redirect.

**Non-Goals:**

- Retrofitting the same fix to `human-admin.ts`'s admin user. The admin user's password is a never-disclosed random value (length 64) and the admin org's `LoginPolicy.userLogin = false` disables the password sign-in form entirely. `changeRequired` never gets exercised on the admin path.
- Upstream-patching `@pulumiverse/zitadel.HumanUser` to add a `passwordChangeRequired` argument. The Dynamic Resource is the conventional escape hatch this project already uses; upstream patching would block on @pulumiverse release cadence and adds no incremental value.
- Production / staging adoption. There is no production `E2eTestUserComponent` (the parent `Zitadel` class is dev-only). When production adopts self-hosted Zitadel, this change's pattern is available to reuse.
- A general-purpose "set password" Dynamic Resource. The new resource specifically marks a password permanent at create-time using an already-known password value; rotating the password through Pulumi is intentionally outside its scope (rotation today is `--replace` on the `HumanUser`, which the existing `ignoreChanges: ['initialPassword']` directive supports).

## Decisions

### D1: Pulumi Dynamic Resource over upstream provider patch

**Choice**: Add `ZitadelHumanUserPasswordPermanent` as a new Dynamic Resource under `dynamic/`. Model it on `smtp-activation.ts` (the closest analogue — both are one-shot state pushes against the Management API).

**Alternatives considered**:

- **Patch `@pulumiverse/zitadel.HumanUser` upstream**: Add a `passwordChangeRequired: false` argument. Rejected — blocks on @pulumiverse release cadence (months), requires forking or a v0.3.0+ migration across the project, and is overkill for a need that one project resource solves locally.
- **Use Pulumi `Command` provider (`local.Command`)**: Shell out to `curl` against the Management API. Rejected — drags in `@pulumi/command` as a new dependency, makes auth (JWT-bearer) a stringly-typed environment-variable dance, and leaks the access token into the command line / process table on the Pulumi runner.
- **Bash script as a post-`pulumi up` hook**: Rejected for the same auth-handling reasons, plus loss of declarative semantics — Pulumi state no longer reflects whether the password is marked permanent.

**Rationale**: The Dynamic Resource pattern is already established (4 resources under `dynamic/`); developers reviewing the new resource have the smtp-activation precedent to compare against. The `zitadelApiCall` helper handles JWT-bearer auth correctly and never logs tokens. Pulumi state records the marker resource, so `pulumi preview` accurately reflects whether the marker is in place.

### D2: Mark password permanent at `create` time, no-op everywhere else

**Choice**: The new resource's CRUD lifecycle is:

- `create`: POST `/management/v1/users/{user_id}/password` with `{ password, noChangeRequired: true }`. Treat any 2xx as success. The Zitadel response shape for the already-permanent no-op case is verified during §1.x live-ops apply (see Open Questions below); the implementation also carries an `isAlreadyPermanent` body-check on non-2xx as a defensive hedge mirroring `smtp-activation.ts`'s `isAlreadyActive` pattern.
- `update`: Re-POST `SetPassword` against the same userId with `news.password` (the value carried from prior state because `password` is suppressed by `ignoreChanges` per the call-site directives — see the Risks-table row at line 103). Only reachable when `domain` or `jwtProfileJson` changes (`password` ignored, `userId` triggers `replaceOnChanges`). Acts as a drift-recovery / re-assertion path: if an operator manually un-marks the password in the Zitadel admin console, the next provider/JWT rotation re-asserts permanence. Preserves `markedAt` from prior state for diff stability.
- `delete`: No-op. There is no `_unset_permanent` verb; removing the Pulumi resource record should not flip the user back to `changeRequired = true`. If true drift handling is needed later, it lives elsewhere (matches the smtp-activation precedent).
- `read`: No-op returning current outputs unchanged. Zitadel's Management API has no `GET /password/state` to query; drift detection is explicitly deferred.

**Alternatives considered**:

- **`create` only, fail on any subsequent diff**: Rejected — would break the domain/jwtProfileJson drift-recovery path and would also fail noisily if the resource's option-shape changes downstream (refactors that re-emit the marker should not require manual state surgery).
- **`update` accepts `news.password` as a rotation channel**: Rejected — would conflict with the `ignoreChanges: ['password']` call-site directive, and rotation is already served end-to-end by `--replace` on the HumanUser cascading through `replaceOnChanges: ['userId']` into a fresh `create()`.
- **`delete` reverts to `changeRequired = true`**: Rejected — there is no Management API endpoint to flip a permanent password back to "must change". Even if there were, calling it on resource removal would be a hostile drift action (admins removing the marker resource for any reason would log everyone out at their next sign-in).

**Rationale**: This matches the established no-op-delete-and-read pattern of `smtp-activation.ts`. The resource captures a one-way state push; drift detection is out of scope for this change.

### D3: Auth via the same `jwtProfileJson` Secret Manager pull as other dynamic resources

**Choice**: The new Dynamic Resource accepts a `jwtProfileJson: pulumi.Input<string>` argument and uses the existing `zitadelApiCall` helper for JWT-bearer auth. The composition root (`Zitadel` class in `cloud-provisioning/src/zitadel/index.ts`) passes through the same `jwtProfileJson` it already reads from GCP Secret Manager for `SmtpComponent`, `ActionsV2Component`, `HumanAdminComponent`. `E2eTestUserComponent` gains a new `jwtProfileJson` parameter on its args.

**Alternatives considered**:

- **Pass the admin SA key path / file location instead of the JSON**: Rejected — diverges from the existing pattern; every other dynamic resource takes the stringified JSON.
- **Re-derive auth inside `permanent-password.ts` from environment variables**: Rejected — couples the resource to Pulumi-runner env wiring and breaks the consistent dependency-injection style of the existing dynamic resources.

**Rationale**: Consistency with the four existing dynamic resources. The JWT profile is already a `pulumi.secret(...)` output in `Zitadel`'s constructor; threading it one level deeper costs one extra arg.

### D4: Pass the password by value, not by reference to the HumanUser resource

**Choice**: `ZitadelHumanUserPasswordPermanent` takes `userId: pulumi.Input<string>` and `password: pulumi.Input<string>` as separate inputs. The caller (`E2eTestUserComponent`) supplies the same ESC value to both the HumanUser's `initialPassword` and this Dynamic Resource. A `dependsOn: [humanUser]` enforces ordering.

**Alternatives considered**:

- **Read the password back from the HumanUser resource's outputs**: Rejected — `zitadel.HumanUser` does not expose `initialPassword` as a readable output (it is write-only). Threading the ESC value through both call sites is the only available path.
- **Have the Dynamic Resource accept the HumanUser pulumi resource directly and pull `userId` from it**: Marginal API ergonomic win, but couples the Dynamic Resource's type signature to a specific @pulumiverse class. Rejected for parity with the smtp-activation / target / user-idp-link / execution dynamic resources, all of which take primitive `pulumi.Input<string>` ids.

**Rationale**: This costs nothing — the caller already has both values literally in scope. The contract is explicit (the caller asserts the two inputs agree) and avoids a brittle "read from another resource's outputs" coupling.

### D5: New `identity-management` requirement, single ADDED block

**Choice**: Add one ADDED requirement "E2E Test User Password Marked Permanent" under `## ADDED Requirements`. Do not MODIFY the existing "Provision Password-Based E2E Test User in Dev Zitadel" requirement.

**Alternatives considered**:

- **MODIFY existing requirement to fold in permanence**: Rejected — the existing requirement correctly describes the HumanUser's provisioning. Permanence is a distinct state push that happens after creation; it deserves its own requirement with its own scenarios.

**Rationale**: One requirement = one resource = one scenario family. Easier to read, easier to validate.

## Risks / Trade-offs

| Risk | Mitigation |
|---|---|
| Zitadel Management API rejects the `SetPassword` call due to policy violation (complexity / history) — would block `pulumi up`. | The password is the same ESC value the HumanUser was already created with; if it satisfied `PasswordComplexityPolicy` at create time it satisfies it at SetPassword time. History policy is currently disabled (verified during the workaround design). If a future policy change tightens this, the failure surfaces loudly at `pulumi up` (not silently as today's drift would). |
| The new resource creates between HumanUser create and the user's first sign-in, leaving a tiny window where `changeRequired = true` is still in effect. | The capture script runs after `pulumi up` completes (developer workflow), so the window is closed before any sign-in attempt. CI doesn't currently exercise the capture flow against a freshly-applied dev stack; if/when it does, the apply→capture sequence is the same. |
| `pulumi destroy` of the new resource leaves the HumanUser with `noChangeRequired = true` (no inverse verb). | Documented as intentional in D2. The HumanUser itself is the source of truth for whether the user exists at all; this resource is a marker for state that Zitadel has no readback for. |
| `dependsOn: [humanUser]` orders creation but does NOT cascade `--replace`. If HumanUser is replaced (new password → new Zitadel snowflake `userId`), the marker's `update()` handler — defined per D2 to accept rotated passwords — would otherwise fire with the new `userId` but the OLD (ignored) `password` value, overwriting the freshly-rotated credential with stale data. | Solved by `replaceOnChanges: ['userId']` on the marker's `CustomResourceOptions`. The HumanUser's new id flows into the marker's `userId` input, triggering destroy + create instead of update. The fresh `create()` runs against the new user with the new password (create-time inputs are not subject to `ignoreChanges`). Paired with `ignoreChanges: ['password']` mirroring the HumanUser's `ignoreChanges: ['initialPassword']` — without this, an ESC-secret edit would be ignored by the HumanUser but would silently trigger the marker's `update()`, rotating the live Zitadel credential outside the rotation protocol. Both directives documented in §2.2 of tasks. |
| Dynamic resource inputs marked `pulumi.secret(...)` at the call site do NOT propagate secret-ness across the resource boundary into outputs — by default, the `outs: { ...inputs, markedAt }` spread would land `password` and `jwtProfileJson` as plaintext in the Pulumi state checkpoint. | The marker resource's constructor explicitly bakes in `additionalSecretOutputs: ['password', 'jwtProfileJson']` via `CustomResourceOptions`, so any caller automatically gets state-side encryption regardless of whether they remember to pass it. A unit test asserts this contract at the constructor boundary so a future refactor that drops the option fails CI. Documented in §1.1 + §1.5 of tasks. |
| Adds one more Zitadel Management API call only when `domain` or `jwtProfileJson` changes — both rare (domain is environment-static, JWT profile rotates only on `rename-zitadel-machine-keys`-style operations). `pulumi up` on unchanged inputs produces no API call (`ignoreChanges` + `replaceOnChanges` together suppress the routine update path). | Bounded latency: one token exchange + one POST per actual change. The smtp-activation precedent fires on the same trigger set without measurable impact. |
| Dev-only gating regression — if someone later removes the `if (env === 'dev')` outer guard, the new resource fires on staging / prod and writes to a Zitadel instance that may not exist there. | Inherits the gating chain: `Zitadel` class guard → `E2eTestUserComponent` synthesis-time guard → the new resource is only instantiated inside the component. No new guard needed; the chain is already defensive-depth (per `playwright-password-test-user` design D-risks). |

## Migration Plan

Dev-only and additive. No data migration.

**Rollout order:**

1. `cloud-provisioning`: add `dynamic/permanent-password.ts`, re-export from `dynamic/index.ts`, wire into `E2eTestUserComponent`, thread `jwtProfileJson` through `E2eTestUserComponentArgs` and the `Zitadel` class. `pulumi preview` on dev: expect `+1 create` (`ZitadelHumanUserPasswordPermanent`) and `~1 update` on `E2eTestUserComponent` (signature change).
2. Apply on dev (`pulumi up`); verify the new resource creates successfully and the Management API call returns 2xx.
3. `frontend`: remove the `[4b/5]` handler block and renumber log lines; re-run `npm run auth:capture:password` against the dev environment; expect no `/password/change` redirect.
4. Verify Playwright E2E suite still passes (`npx playwright test`).
5. Archive the change.

**Rollback**: revert the cloud-provisioning PR — the new Dynamic Resource is destroyed, the HumanUser is left with `noChangeRequired = true` (one-way state). To return to the workaround behavior, the frontend PR's `[4b/5]` block must be restored separately. If both reverts land, the script's idempotent handler degrades gracefully to a no-op (the redirect won't happen since the user is already permanent), so order does not matter and downtime is zero.

## Open Questions

- Empirical response shape for `SetPassword` against an already-permanent password — does Zitadel return 200 (like `_activate` does for already-active SMTP, where re-firing is silently idempotent) or 4xx with a recognizable "no change" / "already set" marker (like `_activate` does for the SMTP "no work to do" case via code 9 / 412)? Verified during §1.x implementation. The implementation ships with both paths handled: the 2xx happy path is the common case, and `isAlreadyPermanent` body-checks non-2xx responses as a defensive hedge. The Open Question exists to record the actual observed shape so that a future audit can prune whichever path is provably unreachable.
