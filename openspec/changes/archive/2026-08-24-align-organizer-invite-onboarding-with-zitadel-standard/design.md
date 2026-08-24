## Context

See proposal.md — Why. This change realigns organizer operator onboarding with
Zitadel's **standard** invitation flow and closes a session-reuse / org-pinning
gap. It supersedes the archived organizer-console decisions **D1** (org-pinned
entry via a URL `org_id`) and **D5** (console-pointed invite), and revises **D7**
+ tracking issue liverty-music/specification#843.

Current shipped state (all in prod): backend v1.39.0 (provisioner creates the
operator via v2 `AddHumanUser` with verified email + no password; login policy
`allowUsernamePassword=true`; invite via `CreateInviteCode(SendInviteCode)` with
a **console** `url_template`); frontend v1.57.5; Zitadel **v4.17.1**. Note the
canonical main specs `organizer-accounts` / `organizer-tenancy` were never
updated for the v1.38.0/v1.39.0 backend fixes, so they still describe the old
"passkey-registration init link" and `allowUsernamePassword=false` — this change
corrects that drift as part of the delta.

Source references (Zitadel `apps/login`): the standard invite UX
([zitadel/zitadel#8310](https://github.com/zitadel/zitadel/issues/8310),
[zitadel/typescript#166](https://github.com/zitadel/typescript/issues/166));
`lib/server/verify.ts` `buildVerificationUrlTemplate`; `lib/server/loginname.ts`;
`lib/server/passkeys.ts` and `lib/client.ts` (@ v4.17.1). Evidence for the
findings below is from a live re-verification on 2026-08-23 (org-test-30 clean
run + Zitadel logs).

## Goals / Non-Goals

**Goals:** one standard "Accept invite" email (click, not type); the invite
credential stays on the IdP surface; the operator lands back on the console after
accepting; the console enforces the authenticated org so a stale/other session
cannot onboard the wrong tenant; correct the stale login-policy spec and the
duplicate-email record.

**Non-Goals:** business screens; email-domain discovery; per-tenant IdP wiring;
a self-serve OTP recovery lane (admin re-invite remains the recovery path);
re-verifying every Zitadel version — this targets v4.17.1 (prod).

## Decisions

**D-A — Invite points at Zitadel's own `/verify`, not the console (Pattern C).**
The provisioner creates the invite with `SendInviteCode` and a `url_template` of
`https://auth.{base}/ui/v2/login/verify?code={{.Code}}&userId={{.UserID}}&organization={{.OrgID}}&invite=true`.
This is the standard form — **proven supported**: the login app's own
`buildVerificationUrlTemplate` (verify-server.ts) builds exactly this shape and
passes it to `createInviteCode`, so those placeholders are first-class. Result:
ONE "Accept invite" email, the operator clicks (never types), the code rides in
the link on the IdP surface (never in a console URL). Drops the console-first
"transport invite" indirection that caused the empty "enter code" screen and the
second email. *Alternative rejected:* keep the console-pointed invite — it is the
source of the UX mismatch and the second email.

**D-B — Return to the console via the tenant login policy `default_redirect_uri`.**
An invite accepted outside any in-flight OIDC request has no `requestId` to
resume, so after passkey setup the login app uses the org's default redirect.
**Proven wiring (v4.17.1):** `lib/server/passkeys.ts` fetches
`getLoginSettings(...).defaultRedirectUri` (L265) and passes it to
`completeFlowOrGetUrl(...)`; in the no-`requestId` branch
(`else if (session?.factors?.user?.loginName)`, L303-308) it calls
`completeFlowOrGetUrl({ loginName, organization }, loginSettings?.defaultRedirectUri)`.
`lib/client.ts` `resolveRedirectUri` priority is: `DEFAULT_REDIRECT_URI` env →
**org-settings `defaultRedirectUri`** → `/signedin` fallback. So setting the
tenant login policy `default_redirect_uri = https://organizer.{base}/`
(via `UpdateCustomLoginPolicy`, which the provisioner already calls) returns the
operator to the console. The console then completes OIDC against the fresh
session → `/welcome`. *Alternative rejected:* set the OIDC app default redirect
or a `DEFAULT_REDIRECT_URI` env — those are instance/app-wide, not per-tenant.

**D-C — Login policy: `allowUsernamePassword=true` (correct the stale spec).**
Already shipped in v1.39.0 and required: the field gates ALL local auth
(username + passkey OR password), so `false` removes the username form and dead-
ends onboarding. Passkey-primary = `PASSWORDLESS_TYPE_ALLOWED` + no password on
the operator. This delta brings `organizer-tenancy` in line with prod.

**D-D — Console enforces the authenticated org (session-reuse fix).** The console
SHALL check the token's org (the org ids in the `urn:zitadel:iam:org:project:roles`
claim) against the intended tenant. On a different-org session it forces
re-authentication (`prompt=login`), rather than admitting the wrong operator. This
closes the reproduced bug where an existing org-test-21 session satisfied
org-test-30's entry.

**The enforcement lives in the route GUARD, not only the callback (corrected after
a prod repro).** The first implementation (fe v1.59.0) put the check only in the
OIDC callback. That was bypassed when a pre-existing console session is admitted
WITHOUT a fresh OIDC exchange: onboarding `org-test-40` with a leftover
`org-test-21` session landed as org-test-21, and Zitadel logs showed **zero console
`/authorize` after the passkey** — the guard admitted the stale session and the
callback (where the check lived) never ran. Fixed in fe **v1.59.1** by moving the
check into the guard (`OrganizerAuthHook`), which runs on every authenticated
route. Verified in prod: the guard now logs "Authenticated org is not the intended
tenant; forcing re-authentication" and redirects to the correct org's login
(`organization=<intended>`). The org signal is the token's org *membership* (any
project-role grant), kept separate from the owner-role gate; a no-grant session
defers to the owner-role gate (→ `/denied`) rather than a re-auth.

**The "intended tenant" signal (resolved — Option 2).** The tenant login policy
`default_redirect_uri` carries this tenant's org id
(`https://organizer.{base}/?org_id=<tenantOrgId>`, set by the provisioner). On
the post-invite landing the console compares the token's org to that `org_id`;
on a match it proceeds to `/welcome` (no extra passkey tap), and only on a
mismatch does it force `prompt=login` (+ `org:id` pin) to re-authenticate as the
correct tenant. *Alternative rejected:* always `prompt=login` on the landing —
safe but costs the just-onboarded operator an extra passkey tap in the normal
case; and trusting any single-org `owner` token does NOT fix the bug (a reused
org-21 token is itself a valid single-org owner token).

**D-E — Correct the duplicate-email record.** Logs proved the duplicate "Zitadel
Login" emails came from **two OIDC authorize flows** (each sending one invite via
the login app's per-mount-guarded `initialSendVerification`), NOT from "/verify
re-firing on every render." Under Pattern C the operator no longer transits
loginname→/verify from the console, so this class of duplicate is largely
designed out; the finding is recorded against #843 and supersedes D7's wording.

## Risks / Trade-offs

- **[Not end-to-end validated] Single email under Pattern C.** Strongly
  source-supported (arriving at `/verify?code=…` carries the code, so loginname's
  server-side `trySendVerification` is not on the path), but not live-tested →
  validate during implementation; log the login-app `CreateInviteCode` count.
- **[Not validated] `DefaultRedirectUri` safe-redirect acceptance.** `client.ts`
  `resolveRedirectUri` runs `isSafeRedirectUri` on the settings value → confirm
  the console origin passes; fall back to `DEFAULT_REDIRECT_URI` env if needed.
- **[Fresh-session org context] After the default redirect the console has no
  `org_id` in the URL.** With D1 removed, the console must derive the org from
  the session/token (the operator authenticated as themselves). Confirm the
  guard/config path works without a URL `org_id` → see Open Questions.
- **[Zitadel notification bug, independent] `could not set notification event on
  aggregate: Errors.User.NotFound`** reproduces for tenant-org operators. It did
  not cause the duplicate and is out of scope here; track separately.

## Migration Plan

1. backend (`organizer-accounts`): change the `CreateInviteCode` `url_template`
   to the Zitadel `/verify` form; set login policy `default_redirect_uri` to the
   console (extend the existing `ensureLoginPolicy` / `UpdateCustomLoginPolicy`).
2. frontend (`organizer-console`): implement the token-org enforcement (D-D);
   handle the default-redirect landing without a URL `org_id`; narrow/retire the
   now-optional `login_hint` handling.
3. Verify E2E on a fresh operator in a clean session: one email, click-not-type,
   `/welcome`, and that a pre-existing other-org session is rejected.
4. Reconcile the archived organizer-console D7 / issue #843 wording.
- **Rollback:** the changes are per-tenant policy + provisioner template + a
  console guard; revert restores the current (working but irregular) flow.

## Open Questions

- None. The "intended tenant" signal for D-D was resolved to Option 2 (the
  tenant `org_id` carried in `default_redirect_uri` + post-callback comparison) —
  see decision D-D.
