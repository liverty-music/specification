## 1. SMTP activation self-healing (cloud-provisioning)

- [x] 1.1 `src/zitadel/dynamic/smtp-activation.ts`: change `read` from no-op to drift-detecting — `POST /admin/v1/smtp/_search`, inspect `state`; return props that differ from recorded state when the config is missing or not `SMTP_CONFIG_ACTIVE` (so refresh reports drift), unchanged when already active. Keep `create`/`update`/`delete` semantics (idempotent `_activate`, no-op delete).
- [x] 1.2 Preserve the single-config assumption + explicit error (>1 config) already in `create`.
- [x] 1.3 `make lint-ts` passes (biome + tsc).

## 2. Environment-specific console redirect (cloud-provisioning)

- [x] 2.1 `src/zitadel/index.ts`: pass `consoleUrl: pulumi.interpolate` `https://${domain}/ui/console` to `new AdminOrgConfigComponent(...)`.
- [x] 2.2 `src/zitadel/components/admin-org-config.ts`: remove the hardcoded dev fallback (or make it the current-env domain) so no env inherits another's console.
- [x] 2.3 `make lint-ts` passes.

## 3. Ship + remediate the live prod instance

- [x] 3.1 Open cloud-provisioning PR; CI green; merge to main. (PR #409 merged)
- [x] 3.2 Prod remediation `pulumi up` (Pulumi Cloud console). (v220 updated redirect LoginPolicy + DefaultLoginPolicy; v221 re-activated SMTP via targeted refresh. Both succeeded 2026-08-18.)
- [x] 3.3 Document targeted `--refresh` requirement: `docs/runbooks/zitadel-smtp-drift.md` added to cloud-provisioning. Covers the safe targeted form (scoped to `smtp-activation`, avoids flaky billing/budget) + Pulumi Cloud console alternative. Full stack refresh remains blocked by the billing/budget resource.

## 4. Verify in prod

- [ ] 4.1 Trigger a Zitadel email (e.g. re-issue an operator passkey link, or an org create in `organizer-accounts`) → prod Postmark server `Liverty Music [prod]` Activity shows the message **Sent/Delivered**. (Deferred: Google SSO only in prod console; passkey email trigger depends on organizer-accounts 6.3 which requires Zitadel console access.)
- [x] 4.2 `curl -sL auth.liverty-music.app/ui/login/` (or a browser) no longer redirects to `auth.dev.liverty-music.app`; it lands on the prod console. (Confirmed 2026-08-18: `GET /` → 302 → `auth.liverty-music.app/ui/login`; Pulumi state shows `defaultRedirectUri=https://auth.liverty-music.app/ui/console` for both policies.)
- [ ] 5.2 Unblock `organizer-accounts` 6.3: complete the operator passkey-link step once prod email delivery is confirmed (4.1).
