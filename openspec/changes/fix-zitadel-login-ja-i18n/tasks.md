## 1. Prepare the Japanese translation payload

- [ ] 1.1 Pull the complete Japanese hosted-login key set from upstream Zitadel `apps/login/locales/ja.json` at the **deployed version tag `v4.14.0`**, and confirm it covers the keys the running login app renders (loginname/title/buttons/accounts/etc.).
- [ ] 1.2 Convert/shape it into the `SetHostedLoginTranslation` `translations` payload (Settings v2 schema). Pin a copy in `cloud-provisioning` (e.g. `src/zitadel/translations/ja.json`) with a comment noting it mirrors upstream `v4.14.0` and is retired once upstream `v2-default.json` ships `ja`.

## 2. Provision the override (cloud-provisioning)

- [ ] 2.1 Add a Pulumi **dynamic resource** (mirroring `src/zitadel/dynamic/`) that calls Settings v2 `SetHostedLoginTranslation` for the `liverty-music` **product org**, `locale = ja`, with the pinned payload, authenticating via the `pulumi-admin` JWT. Make updates idempotent (re-apply on payload change; etag-aware if practical).
- [ ] 2.2 Wire it into the `Zitadel` orchestrator / Frontend component graph (depends on `productOrg`).
- [ ] 2.3 Run `pulumi preview` and confirm only the expected hosted-login-translation add appears (no unintended resource churn). `make check` passes.

## 3. Ship and verify on prod

- [ ] 3.1 Apply through the normal release/ArgoCD/Pulumi flow.
- [ ] 3.2 If the login still serves English after apply, `kubectl rollout restart deploy/zitadel-api-login -n zitadel` to clear the Login UI v2 translation cache (do not conclude failure before the restart).
- [ ] 3.3 Verify via the product OIDC flow with a Japanese preference (`accept-language: ja` and/or the in-login 日本語 selector) that the login renders **Japanese** (titles, labels, buttons) in both light and dark mode, with no English fallback.
- [ ] 3.4 Confirm non-Japanese logins (en, de) are unchanged and the admin/console org login is unaffected.

## 4. Track the permanent upstream fix

- [ ] 4.1 File a Zitadel GitHub issue (and ideally a PR) to add `ja` — plus the other missing languages (`ar, cs, fr, hu, id, ko, mk, pt, ro, sv, tr, uk`) present in `apps/login/locales/` but absent from `internal/query/v2-default.json` — to the backend hosted-login defaults. Link the issue in the override code/comment.
- [ ] 4.2 Record the exit condition: once a deployed Zitadel version includes Japanese defaults, remove the override and re-verify the Japanese login still renders from upstream defaults.
