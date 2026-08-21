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
  and
- call `CreateInviteCode` (v2 User API) with **`SendInviteCode`** and a
  `url_template` that points at the **console** —
  `https://organizer.{base}/?org_id={{.OrgID}}` — and an `application_name` of
  `Liverty Organizer`. Zitadel then sends the "Invitation to Zitadel Login"
  email via its own SMTP (Postmark), whose "Accept invite" link opens the
  console (starting the OIDC flow), never a Zitadel setup page. This is the
  same email/flow the earlier org-test-7 onboarding succeeded with, made
  explicit and console-pointed.

**Why `SendInviteCode` (Zitadel-sent), not `ReturnCode` + a custom backend
email (correcting an earlier assumption):** the backend has **no direct email /
Postmark infrastructure** — its only email path is *through* Zitadel (the
Management API), and `notification_uc` is Web Push, not email. So a custom
backend invitation email is not available without new infrastructure. Letting
Zitadel send the invite via `SendInviteCode` + `url_template` reuses Zitadel's
configured SMTP and requires no new backend email code.

**`login_hint` trade-off:** the Zitadel `SendInviteCode.url_template` exposes
only `UserID`, `OrgID`, `Code` — **no email placeholder** — so the
Zitadel-sent invite link cannot carry `login_hint`. The operator therefore
enters their email once at the Login v2 loginname step, after which Login v2
detects the pending invite and drives passkey setup. The frontend `login_hint`
support (tasks 4.1/4.2, already shipped) is retained as a UX aid for *re-issued*
console links (e.g. a future "email me a sign-in link" or an admin-copied link
that includes `&login_hint=<email>`), not the first Zitadel invite email.

**Confirmed working shape** (verified with the equivalent flow for org-test-7):
invite email → "Accept invite" → console → OIDC (`requestId` preserved through
the redirect) → Login v2 detects the invited user → verification code + passkey
ceremony → finalises the in-flight auth request → `/auth/callback` → `/welcome`.

**Open validation (positive path):** the empty-form dead-end (no invite) is
confirmed, and the org-test-7 completion confirms the invite-driven onboarding
shape. The exact `CreateInviteCode(SendInviteCode, url_template→console)`
combination will be confirmed end-to-end once task 4.3 lands and a fresh org is
driven through in prod.

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
