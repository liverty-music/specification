## Why

Zitadel Cloud has no custom SMTP provider configured, so email verification codes are not sent during Self-Registration. The default Zitadel Cloud SMTP is intended for development and testing only; production requires a dedicated SMTP provider. This change introduces Postmark as the email provider and establishes the email delivery infrastructure.

## What Changes

- Define the Postmark SMTP connection as a `zitadel.SmtpConfig` Pulumi resource and configure it in Zitadel Cloud
- Create dedicated mail subdomains: `mail.liverty-music.app` (prod) / `mail.dev.liverty-music.app` (dev)
- Add DKIM TXT and Return-Path CNAME records to Cloudflare DNS (prod) and GCP Cloud DNS (dev)
- Add a `postmarkServerApiToken` field to `ZitadelConfig` and manage it per environment via Pulumi ESC
- Separate Postmark Servers for dev and prod, each with an independent API token
- Extend the `add-email-claim.js` Zitadel Action to inject the `email_verified` claim into access tokens

## Capabilities

### New Capabilities

- `email-provider`: Postmark SMTP provider configuration, DNS authentication (DKIM / Return-Path), and mail subdomain management

### Modified Capabilities

- `authentication`: Add `email_verified` claim injection to the Zitadel Action. Establish the prerequisite for the Hosted Login Self-Registration flow to perform email verification
- `secret-management`: Add the Postmark Server API Token to Pulumi ESC (stored as a secret)

## Impact

- **cloud-provisioning**: Add SmtpConfig component under `src/zitadel/`, extend ZitadelConfig, modify the Action script, add DNS records (Cloudflare + GCP Cloud DNS)
- **Pulumi ESC**: Add `postmark.serverApiToken` to dev / prod environments
- **Postmark**: Account setup, Server creation (dev / prod), and Sender Signature (domain verification) are manual tasks
- **No impact on existing services**: No backend or frontend code changes required (email_verified enforcement is handled in a separate change `email-verification`)
