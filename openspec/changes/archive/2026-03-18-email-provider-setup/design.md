## Context

Zitadel Cloud's Hosted Login includes an email verification step (OTP code send and entry) during Self-Registration. However, without a custom SMTP provider configured, verification emails are not sent and this step does not function.

The current cloud-provisioning repo manages Zitadel's OIDC app, Login Policy, and Token Actions via Pulumi. SMTP configuration is not yet managed as IaC.

Postmark is adopted as the email provider. A dedicated mail subdomain is created, and DKIM / Return-Path records are configured in DNS to establish delivery authentication.

## Goals / Non-Goals

**Goals:**

- Configure Postmark SMTP in Zitadel Cloud to enable the Hosted Login email verification flow
- Create mail subdomains `mail.liverty-music.app` (prod) / `mail.dev.liverty-music.app` (dev) with DKIM + Return-Path records
- Separate Postmark Servers for dev and prod
- Inject the `email_verified` claim into access tokens so the backend can verify it
- Manage the Postmark Server API Token via Pulumi ESC (stored as a secret)

**Non-Goals:**

- Backend / frontend code changes (handled in a separate change `email-verification`)
- Postmark account creation, Server creation, Sender Signature setup (manual tasks)
- Email template customization (use Zitadel defaults)
- Staging environment setup (dev / prod only)

## Decisions

### 1. Dedicated mail subdomain

Create `mail.liverty-music.app` (prod) / `mail.dev.liverty-music.app` (dev) as mail-specific subdomains.

**Rationale**: Isolate email sending reputation from the web domain. Bounce rate increases or spam classification will not affect `liverty-music.app` itself. If the provider changes in the future, only the mail subdomain DNS records need updating.

**Alternative**: Send directly from the root domain `liverty-music.app`. Simpler but lacks reputation isolation and risks DKIM records conflicting with other DNS records on the root domain.

### 2. DNS record placement

- **prod** (`mail.liverty-music.app`): Cloudflare DNS (added to the existing zone)
- **dev** (`mail.dev.liverty-music.app`): GCP Cloud DNS (because `dev.liverty-music.app` is NS-delegated to GCP Cloud DNS)

**Rationale**: `dev.liverty-music.app` is already NS-delegated from Cloudflare to GCP Cloud DNS. Placing `mail.dev.liverty-music.app` records in Cloudflare would not resolve.

### 3. SMTP credential management

Postmark uses the same Server API Token as both the SMTP username and password. A single config field `postmark.serverApiToken` is stored as a secret in Pulumi ESC and assigned to both the `user` and `password` fields of the `zitadel.SmtpConfig` resource.

**Rationale**: Postmark's SMTP authentication model uses the Server API Token for both fields. Storing it under separate `smtpUser` / `smtpPassword` names would be misleading. A single `serverApiToken` field accurately represents the credential and avoids duplication. GCP Secret Manager + ESO pipeline is unnecessary since Zitadel Cloud connects to SMTP directly (no need to inject into K8s Pods).

**Alternative**: Store `smtpUser` and `smtpPassword` as separate fields. Rejected because they hold the same value, and the naming obscures the fact that Postmark uses a single token.

### 4. Required field in ZitadelConfig

Add `postmarkServerApiToken` as a required field on the `ZitadelConfig` interface.

**Rationale**: SMTP is a prerequisite for email verification and must be configured in all environments. Making it optional risks configuration omissions.

### 5. SmtpConfig component placement

Create `src/zitadel/components/smtp.ts` to manage the `zitadel.SmtpConfig` resource.

**Rationale**: Follows the existing pattern (`frontend.ts`, `token-action.ts`) of separating components by function.

### 6. Extending add-email-claim.js

Add `email_verified` claim injection to the existing `addEmailClaim` Action script instead of creating a new Action.

**Rationale**: Both claims use the same `PRE_ACCESS_TOKEN_CREATION` trigger and the same user object. A separate Action would add TriggerActions management complexity. A single line addition to the existing script suffices.

**Alternative**: Create a separate `addEmailVerifiedClaim` Action. Correct from a separation-of-concerns perspective but not worth the management overhead.

### 7. Sender address design

- dev: `noreply@mail.dev.liverty-music.app`
- prod: `noreply@mail.liverty-music.app`
- Reply-to: Not set (transactional emails; replies are not expected)

## Risks / Trade-offs

**[Postmark Sender Signature verification delay]** — Postmark domain verification requires DNS record propagation, which can take up to 48 hours. Mitigation: Configure dev first and proceed to prod after dev verification succeeds.

**[Zitadel SmtpConfig Pulumi provider limitation]** — The `@pulumiverse/zitadel` SmtpConfig resource lacks an `active` property. Behavior with multiple SMTP configurations is undefined. Mitigation: Create only one SmtpConfig per environment and confirm no existing SMTP configuration exists in the Zitadel Console beforehand.

**[email_verified claim reliability]** — The `email_verified` claim injected via the Zitadel Action depends on the user object's `isEmailVerified` field. A Zitadel bug or API change could produce inaccurate values. Mitigation: The backend treats a missing claim as unverified (fail-closed).

**[Email delivery in dev environment]** — Dev environment emails are actually sent. Test accounts may receive a high volume of emails. Mitigation: Postmark dev Server transactional streams have default rate limits. Adopt an operational convention of using `+dev` suffix for test email addresses.
