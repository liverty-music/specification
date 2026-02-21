## 1. Frontend OIDC Configuration

- [x] 1.1 Add `VITE_ZITADEL_ORG_ID` to `.env` / `.env.development` with the dev org ID
- [x] 1.2 Update OIDC scope in `src/services/auth-service.ts` to include `urn:zitadel:iam:org:id:{orgId}`

## 2. Cloud Provisioning

- [x] 2.1 Update `allowExternalIdp` comment in `cloud-provisioning/src/zitadel/components/frontend.ts` to reflect permanent passkey-only intent

## 3. Verification

- [x] 3.1 Verify sign-in flow shows passkey prompt (no password form)
- [x] 3.2 Verify sign-up flow shows passkey prompt (no external IDP options)
