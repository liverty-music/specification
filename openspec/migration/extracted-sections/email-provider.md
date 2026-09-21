<!-- Extracted 2026-09-21 from openspec/specs/email-provider/spec.md lines 75-103.
     Non-product sections removed so the spec has only Purpose and Requirements.
     Sections: Architecture, Dependencies
     Routed in Phase 1 manifest (OUT:design-doc / OUT:delete). -->

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
