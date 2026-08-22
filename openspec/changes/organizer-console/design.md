## Context

See proposal.md - Why. Mirrors the admin console pattern (bundle-isolated
entry + dedicated hosting) for the organizer surface. Depends on
`organizer-tenancy` (the `organizer-console` OIDC app + per-tenant
passkey-primary login policy). Full design:
[`docs/organizer-platform-design.md`](../../../docs/organizer-platform-design.md).

## Goals / Non-Goals

**Goals:** a bundle-isolated organizer entry, OIDC login via org-pinned
entry, a role-claim route guard, a placeholder, and the dedicated
hosting.

**Non-Goals:** business screens; the organizer API server
(`organizer-rpc-server`); per-org branding; a reception PWA.

## Decisions

**D1 — One OIDC client, org resolved by org-pinned entry (not domain
discovery).** A single `organizer-console` client serves all tenants; the
operator's org is resolved at login by an **org handle** (`org_id` in the URL
or a remembered `org_id`), which the console turns into the Zitadel
`urn:zitadel:iam:org:id:<orgId>` scope. This is why the organizer
`/config.json` omits a fixed `zitadelOrgId` — baking one in would break the
multi-tenant single-app model. Email-domain discovery was dropped from the MVP
in `organizer-tenancy` (redundant, and useless for consumer/gmail operators);
this console implements the org-pinned path instead. A fresh device with no
remembered `org_id` uses an **invitation link** from the backend provisioner
(see D5).

**D2 — Role-claim route guard, backend is source of truth.** Unlike the admin
console (where Google Workspace login *is* the wall), any tenant-org account
authenticates successfully; the console guard therefore inspects the
`organizer-console` project roles claim and admits only `owner`. Real
enforcement is at the backend; the guard is UX.

**D3 — Dedicated hosting mirrors admin-console-hosting.** `organizer.{base}`
host with HTTPRoute + cert + Cloud DNS + per-host `/config.json`; bundle
isolation is enforced the same way as the admin console (consumer chunk
graph contains no organizer module).

**D4 — Consumer config contract unchanged.** The organizer entry defines its
own config shape (this change); the consumer's `frontend-runtime-config`
requirement governs the consumer SPA only and is not modified.

**D5 — First-time sign-in uses an invitation email + Zitadel's OIDC-embedded
invite flow; `CreatePasskeyRegistrationLink` is NOT used.**
`CreatePasskeyRegistrationLink` (the original approach in organizer-accounts)
generates a bare `passkey/set` URL outside any OIDC context. Its registration
code is single-use even on failure due to upstream bug
[#12499](https://github.com/zitadel/zitadel/issues/12499) (unfixed as of
Zitadel v4.14.0 — code marked consumed on first click regardless of whether the
passkey ceremony succeeds), making retries impossible and leaving the operator
stranded on a Zitadel error page with no path back to the console.

Verified live (2026-08-21, hosted Login v2 on Zitadel v4.14.0, prod):

- **The invite EMAIL cannot carry an OIDC auth request.** Neither
  `SendPasskeyRegistrationLink.url_template` nor `SendInviteCode.url_template`
  exposes an `authRequestId` placeholder (only `UserID`, `OrgID`, `Code`,
  `CodeID`). So any email whose link lands on a Zitadel setup page (`passkey/set`
  or the invite-verify page) completes auth-method setup **outside** any auth
  request and dead-ends on the `signedin` page with no way back to the console.
  The onboarding email MUST therefore link to the **console** (which starts the
  OIDC flow), NOT to a Zitadel setup page.
- **Login v2 AUTO-onboards a no-auth-method operator with a verified email — no
  pre-created invite is functionally required** (source-verified against the
  Login v2 app, `apps/login/src` @ `v4.14.0`). In
  [`lib/server/loginname.ts`](https://github.com/zitadel/zitadel/blob/v4.14.0/apps/login/src/lib/server/loginname.ts),
  after the loginName is submitted, when the user has no PASSWORD/PASSKEY/IDP
  method it redirects into the invite flow itself:

  ```ts
  const hasPrimaryMethod = methods.authMethodTypes?.some(
    (m) => m === PASSWORD || m === PASSKEY || m === IDP) ?? false;
  if (!hasPrimaryMethod) {
    const shouldSend = humanUser?.email?.isVerified === true;   // AddHumanUser sets isVerified=true
    return { redirect: `/verify?loginName=…&send=${shouldSend}&invite=true` };
  }
  ```

  Then [`lib/server/verify.ts`](https://github.com/zitadel/zitadel/blob/v4.14.0/apps/login/src/lib/server/verify.ts)
  runs `verifyInviteCode` → `redirect: /authenticator/set` (passkey) →
  `completeFlowOrGetUrl({ sessionId, requestId, … })`, and the **`requestId`
  threads through every step**, so the flow resumes the originating OIDC request
  and returns to the console. Since `AddHumanUser` already sets
  `email.isVerified=true`, `send=true` and Login v2 sends the verification code
  automatically. This is exactly the org-test-7 onboarding.
- **Correction of an earlier misread (the empty loginname card was a login-policy
  bug, NOT a deleted user).** Two live tests showed an *empty* Login v2 loginname
  card. This design previously guessed it was the *no-user-found* branch (a
  deleted operator). That was WRONG — see decision **D6**: the tenant login policy
  set `allow_username_password=false`, which disables the username-entry form
  entirely (that field gates ALL local authentication — username + passkey OR
  password — not just passwords), so with no external IdP configured the operator
  had nothing to click. The empty card was the policy, reproducibly, for a
  perfectly valid operator. Fixed in backend **v1.39.0** (D6). The invite itself
  is still NOT a functional prerequisite; `CreateInviteCode` below is used purely
  as the **email transport** (the backend has no SMTP of its own — see next
  section).

The backend provisioner (organizer-accounts) SHALL therefore:
- remove the `CreatePasskeyRegistrationLink` call (the broken dead-end email),
  and
- call `CreateInviteCode` (v2 User API) with **`SendInviteCode`** — used purely
  as the **email transport** (the backend has no SMTP; Login v2 auto-onboards
  regardless) — and a `url_template` that points at the **console** with the
  org id and email baked in and the code omitted:
  `https://organizer.{base}/?org_id=<zitadelOrgID>&login_hint=<operatorEmail>`,
  plus an `application_name` of `Liverty Organizer`. Zitadel then sends the
  "Invitation to Zitadel Login" email via its own SMTP (Postmark), whose
  "Accept invite" link opens the console (starting the OIDC flow), never a
  Zitadel setup page. This is the same onboarding path the earlier org-test-7
  completion exercised, made explicit and console-pointed.

**Why `SendInviteCode` (Zitadel-sent), not `ReturnCode` + a custom backend
email (correcting an earlier assumption):** the backend has **no direct email /
Postmark infrastructure** — its only email path is *through* Zitadel (the
Management API), and `notification_uc` is Web Push, not email. So a custom
backend invitation email is not available without new infrastructure. Letting
Zitadel send the invite via `SendInviteCode` + `url_template` reuses Zitadel's
configured SMTP and requires no new backend email code.

**`login_hint` CAN be carried** — the `url_template` is a free-form string, and
the operator's email is known at provisioning time, so it is baked in
**statically** (not via a Zitadel placeholder):
`https://organizer.{base}/?org_id=<zitadelOrgID>&login_hint=<operatorEmail>`
(with `<zitadelOrgID>`/`<operatorEmail>` substituted in Go before the call, and
`{{.Code}}` deliberately **omitted** so no credential appears in the link — see
the security note). The frontend `login_hint` support (tasks 4.1/4.2, shipped)
then pre-fills the email and auto-submits the loginname step
(`loginName=<email>&submit=true`, verified in prod v1.57.0), so the operator
skips the email-entry step entirely.

**Security invariant (why `{{.Code}}` is omitted).** The invite/verification
code is an account-takeover-grade secret (whoever redeems it registers the owner
passkey). It MUST stay IdP-side: the console link carries only `org_id` +
`login_hint` (a non-secret email hint), never a code. Login v2 delivers and
consumes the code on the Zitadel surface (`auth.{base}`); the console (a public
SPA) never sees it, so it can't leak via browser history, the `Referer` header,
or access logs. The passkey is registered inside a verified Login v2 session.
This follows the OAuth 2.0 Security BCP (the RP handles no end-user
credentials), OWASP ASVS (no secrets in URLs), NIST 800-63B (authenticator
enrollment in a verified session), and WebAuthn credential binding. Putting the
code in the console URL to save an email was rejected for this reason.

**Confirmed working shape** (org-test-7 completion + the v4.14.0 source trace):
invite email → "Accept invite" → console → OIDC (`requestId` preserved through
the redirect, verified) → Login v2 routes the no-auth operator into `/verify`
→ verification code + passkey → `completeFlowOrGetUrl(requestId)` finalises the
in-flight auth request → `/auth/callback` → `/welcome`.

**VERIFIED end-to-end in prod (2026-08-22, backend v1.39.0 + frontend v1.57.5).**
A fresh, genuinely-uninitialized operator (`org-test-21`) completed the full
path: `CreateInviteCode(SendInviteCode, url_template→console, login_hint baked,
code omitted)` rendered the expected console link → "Accept invite" → console
(org pinned via `org:id` scope, `login_hint` auto-submits the loginname step) →
Login v2 `/verify` (code) → passkey registration → `/auth/callback` →
**`/welcome`** (owner-gated placeholder showing the operator email). Confirmed at
the identity layer too: the tenant login policy read back
`allowUsernamePassword=true` and the operator's only auth method is a passkey.

## D6 — Tenant login policy MUST enable local authentication (`allow_username_password=true`)

**The provisioner originally set `allow_username_password=false`, which broke
onboarding.** Despite its name, that Management-API field (the deprecated alias
of `allow_local_authentication`) gates ALL *local* authentication — logging in
with a username plus a **passkey** OR a password — not just passwords. Zitadel's
own field doc: *"If enabled, users can log in locally with their username and
passkeys or password. Disabling this option will require users to log in with an
external identity provider."* With it `false`, hosted Login v2's loginname page
renders no username-entry form (it gates `<UsernameForm>` on
`allowLocalAuthentication`), and since the tenant org has no external IdP, the
invited operator lands on an empty login card — the onboarding entry point is
gone. This stayed latent until the console-first flow (v1.38.0) exercised the
loginname step directly; an earlier "success" had bypassed loginname via the
pre-v1.38.0 email-direct path.

**Fix (backend v1.39.0):** `ensureLoginPolicy` sets `allow_username_password=true`.
Passkey-primary is achieved by `PasswordlessType=ALLOWED` **plus never setting a
password on the operator** (already the case) — NOT by disabling local auth; with
no password on file the operator's only usable local method remains the passkey,
while the username form renders so they can enter the invite flow.
`AddCustomLoginPolicy` is create-only, so orgs provisioned with the old policy are
converged in place via `UpdateCustomLoginPolicy` on the AlreadyExists path
(idempotent saga). Proven in prod: `org-test-20` (pre-fix) read back
`allowUsernamePassword=false`, `org-test-21` (v1.39.0) read back `true`.

## D7 — Console callback self-heals a cross-context OIDC `state` miss (frontend v1.57.5)

During prod verification, an operator hit a dead-end
`Login failed: No matching state found in storage` after a **successful** passkey
ceremony. Root cause: oidc-client-ts stores the transient signin `state` in the
originating context's `localStorage`; when the callback carries a `state` whose
`signinRedirect` ran in a **different browsing context** (a duplicate
Zitadel-sent invitation opened elsewhere / a second tab — see the duplicate-email
note below), this context never held that state and `signinCallback` throws. The
console rendered a terminal error with no path forward. This is not a systemic
bug — a clean single-context sign-in reaches `/welcome`.

**Fix:** `AuthCallbackRoute` treats that specific error as recoverable and
restarts the OIDC flow **once** from this context (fresh `signinRedirect` writes a
state here; the operator still holds a Zitadel session so it round-trips without
re-auth). Bounded by a one-shot `sessionStorage` flag (fails closed if storage is
unavailable, clears on success) so a genuinely broken store cannot loop.

**Duplicate invitation emails (upstream Zitadel, tracked separately).** Postmark
showed the operator receiving two identical "Invitation to Zitadel Login" emails.
Root cause (confirmed in Zitadel logs): the **backend sends exactly one**
`CreateInviteCode` (`application_name="Liverty Organizer"`); the duplicates are
issued by the **hosted Login v2 app itself**, which re-fires `CreateInviteCode`
(default app name → "Zitadel Login") on every render of `/verify?invite=true`
without a session — the operator's browser loaded that page twice. Not fixable in
our code; filed as an upstream/tracking issue. Harmless (identical links, no code
in the link), and it is the trigger for the multi-context `state` miss that D7
now self-heals.

## Risks / Trade-offs

- **Shared AppConfig type** → if the organizer entry reuses the consumer
  AppConfig type, `zitadelOrgId` must become optional for the organizer
  variant; keep the consumer's required-org contract intact (implementation
  reconciliation, not a consumer spec change).
- **Bundle-isolation regression** → reuse the admin console's chunk-graph CI
  assertion.

## Migration Plan

1. frontend: `organizer.html` entry (bundle-isolated), OIDC via domain
   discovery, role-claim route guard, placeholder; chunk-graph CI assertion.
2. cloud-provisioning: `organizer.{base}` host (HTTPRoute, cert, Cloud DNS) +
   per-host ConfigMap; add the host to the `organizer-console` OIDC app
   redirect URIs.
- Rollback: additive entry + host; remove with no consumer/admin impact.
