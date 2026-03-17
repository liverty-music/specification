# Email Provider Capability

## Purpose

Defines the Postmark SMTP provider configuration, DNS authentication (DKIM / Return-Path), and mail subdomain management for transactional email delivery through Zitadel Cloud.

## Requirements

### Requirement: Zitadel SMTP configuration via Pulumi

The infrastructure SHALL provision a `zitadel.SmtpConfig` Pulumi resource that connects Zitadel Cloud to Postmark's SMTP server. The configuration MUST use `smtp.postmarkapp.com:587` with STARTTLS. Sender address MUST use the mail subdomain (`noreply@mail.<domain>`).

#### Scenario: SmtpConfig resource creation for dev

- **WHEN** the Pulumi dev stack is applied
- **THEN** a `zitadel.SmtpConfig` resource is created with host `smtp.postmarkapp.com:587`
- **AND** `senderAddress` is `noreply@mail.dev.liverty-music.app`
- **AND** `senderName` is `Liverty Music`
- **AND** `tls` is `true`
- **AND** both `user` and `password` are set to the Postmark Server API Token read from ESC config key `postmark.serverApiToken`

#### Scenario: SmtpConfig resource creation for prod

- **WHEN** the Pulumi prod stack is applied
- **THEN** a `zitadel.SmtpConfig` resource is created with host `smtp.postmarkapp.com:587`
- **AND** `senderAddress` is `noreply@mail.liverty-music.app`

### Requirement: Mail subdomain DNS records for DKIM authentication

The infrastructure SHALL create DKIM TXT records and Return-Path CNAME records for Postmark domain authentication. Records for prod MUST be created in Cloudflare DNS. Records for dev MUST be created in GCP Cloud DNS (because `dev.liverty-music.app` is NS-delegated to GCP Cloud DNS).

#### Scenario: Prod DKIM record in Cloudflare

- **WHEN** Postmark provides a DKIM public key for `mail.liverty-music.app`
- **THEN** a TXT record SHALL be created in Cloudflare DNS at `<selector>._domainkey.mail.liverty-music.app`
- **AND** a CNAME record SHALL be created at `pm-bounces.mail.liverty-music.app` pointing to `pm.mtasv.net`

#### Scenario: Dev DKIM record in GCP Cloud DNS

- **WHEN** Postmark provides a DKIM public key for `mail.dev.liverty-music.app`
- **THEN** a TXT record SHALL be created in GCP Cloud DNS at `<selector>._domainkey.mail.dev.liverty-music.app`
- **AND** a CNAME record SHALL be created at `pm-bounces.mail.dev.liverty-music.app` pointing to `pm.mtasv.net`

### Requirement: ZitadelConfig interface extension

The `ZitadelConfig` interface SHALL include `postmarkServerApiToken` as a required string field. This single token is used as both the SMTP username and password, reflecting Postmark's authentication model.

#### Scenario: Missing Postmark token causes type error

- **WHEN** a Pulumi stack is configured without `postmark.serverApiToken` in ESC
- **THEN** TypeScript compilation SHALL fail with a type error

### Requirement: SmtpConfig component isolation

The SMTP configuration SHALL be implemented as a separate component class in `src/zitadel/components/smtp.ts`, following the existing pattern of `frontend.ts` and `token-action.ts`.

#### Scenario: Component instantiation

- **WHEN** the `Zitadel` orchestrator class is constructed
- **THEN** it SHALL instantiate the SMTP component with environment-specific sender address and the Postmark Server API Token
- **AND** the SMTP component SHALL be exposed as a public readonly property

### Requirement: Environment-specific Postmark Server separation

Each environment (dev, prod) SHALL use a separate Postmark Server with an independent Server API Token. The token for each environment SHALL be stored in the corresponding Pulumi ESC environment.

#### Scenario: Dev and prod use different API tokens

- **WHEN** comparing the `postmark.serverApiToken` values across dev and prod ESC environments
- **THEN** the values SHALL be different (each environment has its own Postmark Server token)

## Architecture

### Components

- **SmtpComponent** (`src/zitadel/components/smtp.ts`): Pulumi ComponentResource managing the `zitadel.SmtpConfig` resource
- **Zitadel orchestrator** (`src/zitadel/index.ts`): Instantiates SmtpComponent with environment-specific config

### Configuration

| ESC Key | Description |
|---|---|
| `pulumiConfig.postmark.serverApiToken` | Postmark Server API Token (secret) |

### DNS Records

| Environment | Record Type | Name | Value |
|---|---|---|---|
| prod | TXT | `<selector>._domainkey.mail.liverty-music.app` | DKIM public key |
| prod | CNAME | `pm-bounces.mail.liverty-music.app` | `pm.mtasv.net` |
| dev | TXT | `<selector>._domainkey.mail.dev.liverty-music.app` | DKIM public key |
| dev | CNAME | `pm-bounces.mail.dev.liverty-music.app` | `pm.mtasv.net` |

## Dependencies

- `@pulumiverse/zitadel` - Zitadel Pulumi provider (SmtpConfig resource)
- Postmark SMTP endpoint (`smtp.postmarkapp.com:587`)
- Cloudflare DNS (prod records)
- GCP Cloud DNS (dev records)
