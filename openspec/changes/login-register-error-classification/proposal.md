> **Status: PARKED (proposal-only).** This change is intentionally captured at the proposal stage and held — the scope (owning the registration UI) is large. `design.md` / `specs/` / `tasks.md` are deliberately NOT created yet. Resume with `/opsx:propose` (to generate the remaining artifacts) or `/opsx:explore` (to settle the open design decisions below) when prioritized.

## Why

When a user signs up via the current flow, registration is delegated to Zitadel's **hosted login-v2** page (`auth.liverty-music.app/ui/v2/login/register`, reached via `prompt: 'create'`). That page surfaces **every** failure as a single generic "Could not register user" with an HTTP 500 in the console — it does not distinguish a user-fixable problem (email already registered, invalid input) from a server/infra fault, and it cannot show an actionable message like "this email is already registered — sign in instead."

Root cause (investigated, see archived change `fix-zitadel-login-instance-resolution` follow-up + upstream research): the **Zitadel API already returns correct, distinct gRPC codes** (`AlreadyExists` 409, `InvalidArgument` 400, `FailedPrecondition` 400, …) and login-v2's interceptor even tags each error `isUserError`. The gap is purely in **login-v2's presentation layer**: its register server action (`apps/login/src/lib/server/register.ts`) never catches the `ConnectError`, so it throws → Next.js 500 → a hard-coded generic client message. That UI ships as a **pre-built image** we only deploy (we don't own its source), and Zitadel **config / Custom Login Texts cannot add per-error-code branching** (they only reword static keys). So fixing it in Zitadel's page would require forking + self-building the login image (ongoing maintenance), or an upstream PR (release-cadence dependent, and an explicit "email already registered" message may not be accepted upstream on enumeration grounds).

We instead choose to **own the registration UI** (approach "B") so the registration error UX is fully under our control, without forking Zitadel's image and without waiting on upstream.

## What Changes

- **The app owns the registration entry + error UX** rather than delegating it to Zitadel's hosted register page. The owned flow classifies failures and renders intent-appropriate messages:
  - **User-caused codes → specific, friendly, localized messages.** Per the product decision, this includes an **explicit "this email is already registered" message with a Sign in link** for `AlreadyExists`; field-appropriate guidance for `InvalidArgument`; policy-appropriate text for `FailedPrecondition`; "too many attempts" for `ResourceExhausted`.
  - **Server-caused codes (`Internal`, `Unknown`, `Unavailable`, `DeadlineExceeded`, `DataLoss`, `Unimplemented`) → a single generic message that hides internal detail**, with the full error logged server-side only.
- **Enumeration guards (accepted tradeoff).** Showing "email already registered" on signup is a deliberate, bounded account-enumeration oracle. It is permitted ONLY with: **rate-limiting + CAPTCHA/bot-mitigation** on the existence check, and **login / password-reset responses kept generic**. (Product decision: explicit message chosen over the generic "if you have an account, sign in" alternative.)
- **No fork of Zitadel's login image; no reliance on config-only reword.** Zitadel's hosted register remains a fallback for users who reach it directly; closing that residual path (via a thin upstream PR or a generic `SetHostedLoginTranslation` reword) is out of scope here and tracked separately.

## Capabilities

### New Capabilities

- `registration-error-ux`: The app-owned signup/registration flow's error-classification and messaging contract — mapping Connect/gRPC error codes to user-facing copy (user-code → specific incl. explicit email-exists; server-code → generic/hidden), plus the enumeration-guard requirements (rate-limit, CAPTCHA, generic login/reset).

### Modified Capabilities

- `user-auth`: The "Sign Up / Sign In" requirement changes — registration no longer simply redirects to Zitadel's hosted register form via `prompt: 'create'` and accepts its generic error UX; the app SHALL own the registration error presentation per `registration-error-ux`. (Exact delta deferred to the specs phase.)

## Impact

- **Repos**: `frontend` (Aurelia signup flow + error UI + i18n), `backend` (an email-availability / pre-check RPC with rate-limiting; classified-error mapping if registration is proxied through our API), `specification` (this spec + `user-auth` delta). NOT `cloud-provisioning` for the core change (no Zitadel image fork).
- **Security**: introduces a deliberate, rate-limited enumeration surface on signup; REQUIRES login/reset to stay generic. Threat-model note: if Liverty Music membership is treated as sensitive, this decision should be revisited.
- **Dependency**: Zitadel Session/User v2 APIs remain the source of truth for account creation; the app wraps them rather than replacing identity logic.
- **Open design decisions (to resolve in `design.md` when un-parked)**:
  1. **b1 vs b2** — (b1) collect email in our Aurelia app, pre-check existence via a rate-limited backend RPC, show our message, THEN hand off to Zitadel for the passkey ceremony; vs (b2) a fully app-owned login/registration UI built on Zitadel's Session/User v2 APIs (heavier, covers the whole ceremony).
  2. **Residual direct-hit coverage** — how much to invest in the "user lands on Zitadel's hosted register directly" path (upstream PR vs generic reword vs accept).
  3. **Bot mitigation** choice (CAPTCHA vendor vs alternative) and rate-limit budget for the existence check.
