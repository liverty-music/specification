## 1. SMTP activation self-healing (cloud-provisioning)

- [ ] 1.1 `src/zitadel/dynamic/smtp-activation.ts`: change `read` from no-op to drift-detecting — `POST /admin/v1/smtp/_search`, inspect `state`; return props that differ from recorded state when the config is missing or not `SMTP_CONFIG_ACTIVE` (so refresh reports drift), unchanged when already active. Keep `create`/`update`/`delete` semantics (idempotent `_activate`, no-op delete).
- [ ] 1.2 Preserve the single-config assumption + explicit error (>1 config) already in `create`.
- [ ] 1.3 `make lint-ts` passes (biome + tsc).

## 2. Environment-specific console redirect (cloud-provisioning)

- [ ] 2.1 `src/zitadel/index.ts`: pass `consoleUrl: pulumi.interpolate` `https://${domain}/ui/console` to `new AdminOrgConfigComponent(...)`.
- [ ] 2.2 `src/zitadel/components/admin-org-config.ts`: remove the hardcoded dev fallback (or make it the current-env domain) so no env inherits another's console.
- [ ] 2.3 `make lint-ts` passes.

## 3. Ship + remediate the live prod instance

- [ ] 3.1 Open cloud-provisioning PR; CI green; merge to main.
- [ ] 3.2 Run a **refreshing** prod `pulumi up` (Pulumi Cloud console, `--refresh` enabled): SMTP `read`/refresh detects drift → `_activate` re-runs → `SMTP_CONFIG_ACTIVE`; admin-org LoginPolicy `defaultRedirectUri` updates to the prod console.
- [ ] 3.3 Enable refresh on the prod deployment (if the console supports it) OR document the `pulumi up --refresh` requirement in the runbook so future SMTP drift self-heals.

## 4. Verify in prod

- [ ] 4.1 Trigger a Zitadel email (e.g. re-issue an operator passkey link, or an org create in `organizer-accounts`) → prod Postmark server `Liverty Music [prod]` Activity shows the message **Sent/Delivered**.
- [ ] 4.2 `curl -sL auth.liverty-music.app/ui/login/` (or a browser) no longer redirects to `auth.dev.liverty-music.app`; it lands on the prod console.
- [ ] 4.3 Confirm dev is unaffected (dev `defaultRedirectUri` still the dev console; dev SMTP still active).

## 5. Post-remediation hygiene

- [ ] 5.1 Rotate the prod Postmark Server API Token (it was shared in plaintext during diagnosis); update ESC `postmark.serverApiToken` for prod; re-`pulumi up` if needed.
- [ ] 5.2 Unblock `organizer-accounts` 6.3: complete the operator passkey-link step now that prod email delivers.
