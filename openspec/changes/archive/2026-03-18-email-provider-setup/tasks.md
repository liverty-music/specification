## 1. Postmark manual setup

- [x] 1.1 Create the dev Server (`liverty-music-dev`) in the Postmark account
- [x] 1.2 Create the prod Server (`liverty-music-prod`) in the Postmark account
- [x] 1.3 Add the domain `mail.dev.liverty-music.app` as a Sender Signature on the dev Server
- [x] 1.4 Add the domain `mail.liverty-music.app` as a Sender Signature on the prod Server

## 2. DNS record configuration

- [x] 2.1 Create a Pulumi resource that adds the dev DKIM TXT record to GCP Cloud DNS (`dev.liverty-music.app` zone)
- [x] 2.2 Add the dev Return-Path CNAME record (`pm-bounces.mail.dev.liverty-music.app` -> `pm.mtasv.net`) to GCP Cloud DNS
- [x] 2.3 Create a Pulumi resource that adds the prod DKIM TXT record to Cloudflare DNS
- [x] 2.4 Add the prod Return-Path CNAME record (`pm-bounces.mail.liverty-music.app` -> `pm.mtasv.net`) to Cloudflare DNS
- [x] 2.5 Confirm DNS verification succeeds for both domains in Postmark

## 3. Pulumi ESC configuration

- [x] 3.1 Set the dev Postmark Server API Token via `esc env set liverty-music/dev pulumiConfig.postmark.serverApiToken --secret`
- [x] 3.2 Set the prod Postmark Server API Token via `esc env set liverty-music/prod pulumiConfig.postmark.serverApiToken --secret`

## 4. Zitadel SmtpConfig component

- [x] 4.1 Add `postmarkServerApiToken: string` to the `ZitadelConfig` interface (`src/zitadel/index.ts`)
- [x] 4.2 Create `src/zitadel/components/smtp.ts` and implement the `SmtpComponent` class
- [x] 4.3 Instantiate `SmtpComponent` in the `Zitadel` orchestrator class
- [x] 4.4 Implement per-environment sender address mapping (dev: `noreply@mail.dev.liverty-music.app`, prod: `noreply@mail.liverty-music.app`)

## 5. Zitadel Action extension

- [x] 5.1 Add `email_verified` claim injection to `add-email-claim.js` (`api.v1.claims.setClaim('email_verified', user.human.isEmailVerified)`)
- [x] 5.2 Confirm the machine user guard also applies to the `email_verified` claim

## 6. Verification

- [x] 6.1 Confirm dev stack changes with `pulumi preview -s dev`
- [x] 6.2 Confirm `make check` (lint-ts) passes
- [x] 6.3 Deploy to dev and confirm that the email verification code is delivered during Self-Registration
- [x] 6.4 Confirm the `email_verified` claim is included in the access token
