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
- **An invite code is REQUIRED for Login v2 to onboard a passwordless-only
  operator.** Driving the clean console → OIDC path for a bare operator
  (`AddHumanUser`, verified email, no passkey, **no invite code**) renders an
  **empty Login v2 loginname form** — no input, no button, no way to proceed
  (reproduced with and without `login_hint`). With `allow_username_password=false`
  and `allow_register=false`, Login v2 has no auth method to offer and no invite
  to redeem. `CreatePasskeyRegistrationLink` is NOT an invite; its code is
  single-use-on-failure (`#12499`) and it dead-ends via the email path above.
- **Confirmed working shape:** the console → OIDC (`requestId` preserved through
  the redirect, verified) → Login v2 detects the **invited** user → sends a
  verification-code email → code + passkey ceremony → finalises the in-flight
  auth request → `/auth/callback` → `/welcome`. `login_hint` pre-fills the email
  and auto-submits the loginname step (verified: `loginName=<email>&submit=true`).

The backend provisioner (organizer-accounts) SHALL therefore:
- remove the `CreatePasskeyRegistrationLink` call (the broken dead-end email),
- call `CreateInviteCode` with **`ReturnCode`** (NOT `SendCode`) so Login v2 can
  drive first-auth-method setup for the invited operator. `ReturnCode` creates
  the invited state WITHOUT Zitadel sending its own "Invitation to Zitadel Login"
  email — which would be a redundant third email whose link dead-ends anyway.
  The returned code is **discarded**: the backend needs only the invite to
  *exist*; Login v2 delivers the redemption OTP to the operator's verified email
  at onboarding time (see D6). And
- send a custom invitation email (via the existing Postmark notification
  infrastructure) whose link is the **console** URL with
  `?org_id=<id>&login_hint=<email>` — never a Zitadel setup-page URL.

The `login_hint` is passed through the OIDC authorization request to pre-fill
the operator's email in Zitadel's login page, eliminating one manual input step.

**Open validation (positive path):** the empty-form dead-end (no invite) is
confirmed; the positive path (invite code present → onboarding completes →
`/welcome`) will be confirmed end-to-end once task 4.3 lands `CreateInviteCode`
and a fresh org is driven through. The design is grounded on the confirmed
negative result + the Zitadel docs (CreateInviteCode is the canonical B2B
invite API) + the earlier org-test-7 completion.

**D6 — Onboarding secret handling: IdP-owned redemption; the invite secret
never enters an app URL (security).** The invite code grants first-auth-method
setup — whoever holds it can register the owner passkey — so it is an
account-takeover-grade secret, handled like a password-reset token. Three shapes
were considered:

- **A (CHOSEN) — console-first, IdP-owned redemption.** The invitation email
  carries only the console URL (`?org_id=&login_hint=`) with NO secret; the
  operator enters via OIDC; Login v2 sends the redemption OTP to the verified
  email and consumes it on the IdP surface (`auth.{base}`). The app never sees
  the secret.
- **B (REJECTED) — `SendCode` url_template → console, code in the URL.** Puts
  the secret in a public-SPA URL → leaks via browser history, the `Referer`
  header (to the console's third-party loads: fonts, analytics), and
  access/CDN logs. Also non-functional: no standard channel hands a URL-borne
  code to hosted Login v2.
- **C (REJECTED) — console calls `VerifyInviteCode` client-side with the URL
  code.** Same secret-in-URL leak, PLUS a client-side redemption that opens a
  "verified-invite / no-passkey" window: an attacker who captured the leaked
  code could register *their* passkey (account takeover). It also forces the
  console into a custom-login-UI role, widening the frontend attack surface.

Consequence: **two emails, by design.** Email 1 = our custom invitation (console
URL, no secret). Email 2 = Login v2's redemption OTP (IdP-side; the app never
touches it). The OTP is NOT a redundant re-verification of the already-verified
email — it is a *fresh possession check at credential binding* (only whoever
controls the mailbox at onboarding time can register the passkey), consistent
with the mailbox being the account's root of trust. Aligns with the OAuth 2.0
Security BCP (the RP does not handle end-user credentials), OWASP ASVS (no
secrets in URLs; single-use short-TTL, server-side verification), NIST 800-63B
(authenticator enrollment in a verified session), and WebAuthn credential
binding. B/C trade these guarantees for one fewer email — a bad trade.

**D7 — Invite lifecycle & idempotency.** The invite code is short-lived
(observed TTL ~1h) and single-use. If the operator does not onboard before it
expires, Login v2's "Resend code" reissues one, and the provisioner's reconcile
loop (re-running `ensureOperatorUser`) re-creates the invite on the next pass —
so a stale invite self-heals. `CreateInviteCode` MUST be idempotent-safe in the
provisioning saga: re-invoking for an already-invited, still-uninitialized
operator is acceptable (the new pending invite supersedes the old). Once the
operator has registered a passkey they are *initialized*; subsequent sign-ins
need no invite and no OTP (returning-operator path), so the provisioner MUST NOT
re-invite an initialized operator.

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
