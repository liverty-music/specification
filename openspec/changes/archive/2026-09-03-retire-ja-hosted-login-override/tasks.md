## 1. Confirm the upstream fix and merge semantics

- [x] 1.1 Confirm Zitadel ships Japanese in `internal/query/v2-default.json` and identify the first version. Present from **v4.17.0** (v4.16.0 has 11 langs / no `ja`; v4.17.0+ has 15 langs incl. `ja`, 296 keys); prod runs v4.17.1.
- [x] 1.2 Confirm the merge semantics so a slimmed override is safe. `GetHostedLoginTranslation` (`internal/query/hosted_login_translation.go`) merges org → instance → system via `mergo.Merge` (fills only missing keys), and `getSystemTranslation(ja, en)` now returns the real Japanese system default — so keys absent from an override back-fill from Japanese, not English.
- [x] 1.3 Measure drift: pinned `en`/`ja` vs v4.17.1 differ by exactly one key (`idp.signInWithZitadel`, which already resolves from the login bundle); `en` system default == login-bundle `en.json` (0 value diffs) → slimming is behavior-preserving.

## 2. Slim the overrides (cloud-provisioning)

- [x] 2.1 Reduce the English override to the two rebrand keys (`common.title`, `register.description`) inline; back-fill the rest from the system default. Remove vendored `src/zitadel/translations/en.json`.
- [x] 2.2 Empty the Japanese override (`translationsJson = '{}'`) to neutralize the historical full override via an upsert (no reset RPC; provider `delete()` is a no-op). Remove vendored `src/zitadel/translations/ja.json`.
- [x] 2.3 Drop the biome ignore entry for `src/zitadel/translations/**`; update the component and dynamic-provider doc comments. `make lint-ts` passes. Opened as `cloud-provisioning` PR.

## 3. Apply and verify on prod

- [x] 3.1 Run `pulumi preview` for prod and confirm the only hosted-login changes are the `ja` override → empty and the `en` override → 2 keys (no unrelated churn). Prod update v240 diff = `same:407 / update:4` — the two hosted-login overrides plus the two pre-existing recurring drifts (`dashboard-zitadel-observability`, `organizer-media-backend-bucket`); a read-only `pulumi preview` after apply shows the two overrides with zero diff (applied/stable).
- [x] 3.2 Apply via the manual prod `pulumi up`, then `kubectl rollout restart deploy/zitadel-api-login -n zitadel` to clear the login translation cache. Prod update v240 succeeded (gitHead = merge commit of cloud-provisioning #476); `zitadel-api-login` rolled out with no downtime.
- [x] 3.3 Verify via the product OIDC flow: `ja` renders Japanese (no English fallback), `en` login/register shows the "Liverty Music" rebrand, `de` unchanged, and the admin/console org login is unaffected. Browser-verified on `auth.liverty-music.app` (product org): `ja` → 「お帰りなさい！」/「ログイン情報を入力してください。」; `en` → "Welcome back!"/"Enter your login details." (no key leakage, no "Zitadel" string); `de` → "Willkommen zurück!". `register.description` not observable (prod has `allowRegister=false` → "Registration disabled"), but its value is unchanged by this change (only the supply path changed, full → 2-key).

## 4. Close out

- [ ] 4.1 Close the upstream tracking issue zitadel/zitadel #12230 as resolved in v4.17.0. Deferred: intentionally waiting for the maintainer window before closing (see the follow-up comment posted 2026-09-03).
