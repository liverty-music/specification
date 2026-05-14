## Why

`playwright-password-test-user`'s archived [Implementation Deltas](https://github.com/liverty-music/specification/tree/main/openspec/changes/archive/2026-05-14-playwright-password-test-user/design.md) flagged a structural gap:

- `@pulumiverse/zitadel.HumanUser` v0.2.0 sets a user's `initialPassword` with Zitadel's default credential state — `changeRequired = true`. First sign-in redirects to `/ui/v2/login/password/change` and refuses to issue tokens until the user changes the password.
- The provider exposes no knob to flip this flag at create time. The Pulumi-side fix would require a SetPassword API call after HumanUser creation.
- The frontend `capture-auth-state-password.ts` script works around this with an in-script handler that detects the redirect and re-submits the current password as the "new" one. The workaround is documented in the script comments and in `playwright-password-test-user`'s tasks.md follow-up note.

That workaround is fragile in three ways:

1. **Depends on Zitadel's default password-history policy.** Today the policy has no `historySize` constraint, so `new = current` is accepted. If a future Zitadel policy change enables history checking, the workaround silently breaks on the first capture-script run after that change.
2. **Re-submission flow has two extra navigations** (POST `/password/change` → GET `/password/change` follow-up → eventual OIDC redirect). Each adds latency and a failure surface to the script.
3. **The contract is hidden.** A new developer reading `capture-auth-state-password.ts` sees a "[4b/5] Clearing first-sign-in password-change prompt…" log line with no obvious explanation; the rationale lives in a comment block that's easy to miss.

The proper fix is to drive Zitadel into the desired state at provision time via a Pulumi Dynamic Resource — same pattern the project already uses for `ZitadelSmtpActivation`, `ZitadelTarget`, `ZitadelExecutionFunction`, `ZitadelUserIdpLink` (all in `cloud-provisioning/src/zitadel/dynamic/`). Add one more: `ZitadelHumanUserPasswordPermanent`.

## What Changes

- **Add Pulumi Dynamic Resource** `ZitadelHumanUserPasswordPermanent` in `cloud-provisioning/src/zitadel/dynamic/permanent-password.ts`. Calls Zitadel Management API `POST /management/v1/users/{user_id}/password` with `{ password, noChangeRequired: true }` after the HumanUser is created. Lifecycle: `create` posts; `update` re-asserts permanence on drift recovery (only reachable when `domain` / `jwtProfileJson` changes — the call-site directives `ignoreChanges: ['password']` + `replaceOnChanges: ['userId']` route password rotation through a fresh `create()` instead); `delete` and `read` are no-ops (the call is a one-shot state push; nothing to GET, no inverse `_unset_permanent` verb).
- **Wire the new Dynamic Resource into `E2eTestUserComponent`** so the `e2e-test-password` HumanUser receives `noChangeRequired = true` immediately after Pulumi creates it. The same ESC password is passed to both the HumanUser's `initialPassword` field and the new Dynamic Resource — they always agree.
- **Remove the in-script workaround from `frontend/scripts/capture-auth-state-password.ts`** — the `if (page.url().includes('/password/change'))` block (and its surrounding helper code) is no longer needed once the Pulumi-side fix is live. Script progress logs revert to `[1/4]–[4/4]` (the `[4b/5]` step disappears).

## Capabilities

### Modified Capabilities

- `identity-management`: ADD one requirement — "E2E Test User Password Marked Permanent" — specifying that the dev e2e-test-user's password SHALL be marked permanent (`noChangeRequired = true`) at Pulumi-apply time, with scenarios covering the first-sign-in flow and the password-rotation path.

### New Capabilities

None. The new Dynamic Resource is implementation, not a capability — it satisfies the new `identity-management` requirement above.

### Removed Capabilities

None.

## Impact

**Affected repositories**

- `cloud-provisioning/src/zitadel/dynamic/permanent-password.ts`: new Dynamic Resource (~100 lines, modeled after `smtp-activation.ts`).
- `cloud-provisioning/src/zitadel/dynamic/index.ts`: re-export the new resource.
- `cloud-provisioning/src/zitadel/components/e2e-test-user.ts`: add a `ZitadelHumanUserPasswordPermanent` instance wired after the `HumanUser` create, with the same password input and `dependsOn: [humanUser]`.
- `frontend/scripts/capture-auth-state-password.ts`: drop the `[4b/5]` password-change handler block (~25 lines) plus its surrounding documentation comments. Renumber `[5/5]` → `[4/4]`.

**Affected systems**

- Dev Zitadel: gains a Management API call sequence at `pulumi up` time (`AddHumanUser` → `SetPassword(noChangeRequired=true)`). The HumanUser is observed to no longer redirect to `/password/change` on first sign-in.
- E2E pipeline: capture-script flow shortens from 5 steps to 4. No semantic change in storage state output.

**Reversibility**

- Single revert of the cloud-provisioning PR removes the Dynamic Resource and undoes the wiring; the next `pulumi up` cleanly destroys the marker resource. The HumanUser itself is untouched — its `noChangeRequired` flag stays whatever it was at the time of revert (the Management API has no `_unset_permanent` verb, by design). To return to the workaround state intentionally, the frontend script's `[4b/5]` block must be restored in a separate commit.
- Single revert of the frontend PR restores the in-script workaround. Idempotent against either Pulumi state — the workaround simply becomes a no-op when the page does not redirect to `/password/change`.

**Dependencies**

- Requires `playwright-password-test-user` archived (it is — provides the `E2eTestUserComponent` this change extends).
- Requires `remove-passkey-capture-path` archived (it is — confirms the password capture flow is the only consumer of the test user; the workaround block was added against the password-capture script that this change is simplifying).

**Out of scope**

- Retrofitting the same fix to `human-admin.ts`'s admin user. That user's password is a never-disclosed random value and the admin org's `LoginPolicy.userLogin = false` disables the password sign-in form entirely; `changeRequired` never gets exercised on the admin path, so no fix is needed there.
- Patching `@pulumiverse/zitadel.HumanUser` upstream to add a `passwordChangeRequired` argument. The Dynamic Resource is the conventional escape hatch here; upstream patching is out of scope and would block on @pulumiverse release cadence.
- Production / staging adoption. There is no production `E2eTestUserComponent` (the parent `Zitadel` class is dev-only); when production adopts self-hosted Zitadel, this change's pattern will be available for it to reuse.
