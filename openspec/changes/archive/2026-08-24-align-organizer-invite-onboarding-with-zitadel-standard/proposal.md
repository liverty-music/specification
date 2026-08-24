## Why

The shipped organizer operator onboarding deviates from Zitadel's standard
invite flow, producing a confusing UX and a tenant-isolation bug. A live
re-verification (2026-08-23, backend v1.39.0 / frontend v1.57.5 / Zitadel
v4.17.1) established, with logs and source, three problems:

1. **UX mismatch.** The backend sends its own "Liverty Organizer" transport
   invite pointing at the **console**, which starts OIDC and lands the operator
   on Zitadel's `/verify` **without the code**, so they see an empty "enter the
   code" screen. Hosted Login v2 then sends a **second** "Invitation to Zitadel
   Login" email whose link is a "click Accept invite" button (code embedded in
   the link, not shown as text). The screen says "type a code"; the email says
   "click a button" — they contradict each other. Zitadel's standard invite is
   ONE "Accept invite" email whose link opens `/verify?code=…&invite=true`
   directly (code in the link, click-not-type) — see zitadel/zitadel#8310 and
   zitadel/typescript#166.

2. **Tenant-isolation / org-pinning bug (security-relevant).** Opening a fresh
   operator's invite while an unrelated Zitadel session already exists in the
   browser **reuses that session** — the `urn:zitadel:iam:org:id:<id>` scope is
   a hint Zitadel ignores when a session exists, and prod does not force
   re-authentication (`prompt=login` is dev-only). The operator is then
   authenticated as the **wrong org** and the genuine invite is silently
   swallowed. Not a cross-user data breach (backend authz is per-token), but a
   real org-pinning enforcement gap that must be closed before business screens.

3. **Corrections to prior records.** The earlier "duplicate invite emails" were
   proven (Zitadel logs) to come from **two OIDC authorize flows**, each
   legitimately sending one invite — NOT from "/verify re-firing on every
   render." The tracking issue liverty-music/specification#843 and the archived
   organizer-console design D7 must be corrected.

## What Changes

- **Adopt Zitadel's standard invite flow (Pattern C).** The provisioner creates
  the invite with a `url_template` pointing at Zitadel's own login `/verify`
  (`/verify?code={{.Code}}&userId={{.UserID}}&organization={{.OrgID}}&invite=true`)
  instead of the console — ONE "Accept invite" email, click-not-type, and the
  code stays on the IdP surface (`auth.{base}`), never in a console URL.
- **Return the operator to the console after acceptance via the tenant login
  policy's `default_redirect_uri`.** Set it to `https://organizer.{base}/`. After
  passkey setup with no OIDC request in flight, Login v2 redirects there
  (source-verified wiring; see design). The console then completes OIDC (fresh
  session) → `/welcome`.
- **BREAKING (onboarding model): drop console-first org-pinned entry.** The
  console no longer relies on an `org_id` URL param to pin the org on first
  sign-in (D1) nor on a console-pointed invite (D5). The invite code (bound to
  the operator) carries org context; the console derives the org from the token.
- **Fix the session-reuse / org-pinning bug.** The console enforces that the
  authenticated token's org matches the intended tenant; a mismatched or reused
  session forces re-authentication (or sign-out) rather than silently admitting
  the wrong operator.
- **Correct prior records.** Reconcile the duplicate-email cause (two authorize
  flows) in the affected spec text and note it against issue #843.

## Capabilities

### New Capabilities
<!-- None. This change modifies existing, already-archived capabilities. -->

### Modified Capabilities
- `organizer-accounts`: the "Initial operator bootstraps credentials on first
  sign-in" requirement — the invite is created with a Zitadel-standard
  `/verify` `url_template` (one email, click-not-type), replacing the
  console-pointed transport invite.
- `organizer-tenancy`: the "Organizer tenant orgs use a passkey-primary login
  policy…" requirement — the tenant login policy additionally sets
  `default_redirect_uri` to the organizer console so invite/passkey completion
  returns to the console.
- `organizer-console`: the "Authenticate operators via org-pinned entry…" and
  "login_hint pre-fill…" requirements — first-time entry is via the login-policy
  default redirect after invite acceptance (not a console-pointed link or a
  fixed `org_id` URL param); the console enforces the session's org matches the
  intended tenant (closing the session-reuse gap).

## Impact

- **backend** (`organizer-accounts` provisioner,
  `internal/infrastructure/zitadel/organizer_provisioner.go`): change the
  `CreateInviteCode` `url_template`; set the login policy `default_redirect_uri`.
  No new email/SMTP infrastructure.
- **frontend** (`organizer-console`): entry/guard/callback handling for the
  default-redirect landing and the org-match enforcement; the `login_hint` role
  narrows.
- **cloud-provisioning / organizer-tenancy**: none expected beyond the login
  policy field, which the backend provisioner sets at runtime.
- No proto changes. Supersedes archived organizer-console decisions D1 and D5;
  revises D7 and tracking issue liverty-music/specification#843.
- Prod stack: Zitadel v4.17.1 (server-side invite send via `trySendVerification`,
  `codeSent` verify flag), backend v1.39.0, frontend v1.57.5. Tracked under
  liverty-music/specification#759 (roadmap step ①).
