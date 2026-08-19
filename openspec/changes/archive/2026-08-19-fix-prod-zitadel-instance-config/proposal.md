## Why

Two prod-only Zitadel instance-config defects, both surfaced while verifying
`organizer-accounts` 6.3 (operator passkey onboarding), block all Zitadel email
delivery and misroute the console. Neither is organizer-specific — they affect
every Zitadel email (verification, password reset, passkey init) and every
context-less Console login in prod.

1. **SMTP is silently inactive in prod.** `SendPasswordlessRegistration` is
   accepted but no email reaches Postmark (0 sends on both the prod and dev
   Postmark servers). The `ZitadelSmtpActivation` dynamic resource activated the
   config once (2026-05-15) but its lifecycle is, by current spec, a **no-op on
   unchanged inputs** (no `read`, no re-activation) — so once the live
   activation drifts (a rebuild/reset/out-of-band deactivation that does not
   change the Pulumi inputs), Pulumi never notices and never re-activates. The
   failure is invisible: the send API returns success and nothing logs an error.

2. **Console login redirects to the dev console in prod.**
   `auth.liverty-music.app/ui/login/` 302-redirects to
   `https://auth.dev.liverty-music.app/ui/console`. The admin org LoginPolicy's
   `defaultRedirectUri` is set by `AdminOrgConfigComponent`, which falls back to a
   hardcoded dev URL when no `consoleUrl` is passed — and the prod call site
   (`src/zitadel/index.ts`) does not pass one. So prod (and dev) both get the dev
   console URL.

## What Changes

- **Make SMTP activation self-healing.** Change `ZitadelSmtpActivation` so its
  `read` handler queries the live SMTP config's activation state and reports
  drift when it is not `SMTP_CONFIG_ACTIVE`, so `pulumi up` (with refresh)
  re-activates it. A runtime deactivation must no longer be a permanent silent
  outage. Preserve create-time idempotency (already-active = success).
- **Wire the environment-specific console URL.** Pass `consoleUrl` to
  `AdminOrgConfigComponent` from the per-environment domain so the admin org
  LoginPolicy `defaultRedirectUri` is the correct console for the environment
  (prod → `https://auth.liverty-music.app/ui/console`); remove reliance on the
  hardcoded dev fallback.
- **Remediate the live prod instance:** re-activate the prod SMTP config and
  correct the prod `defaultRedirectUri` via `pulumi up`; confirm Postmark shows a
  delivered email and the prod console no longer redirects to dev.

Explicit non-goals: no changes to the Postmark account/DNS (prod server + domain
are verified), no new email templates, no organizer-domain code changes.

## Capabilities

### Modified Capabilities
- `identity-management`: the SMTP activation requirement gains a self-healing
  (drift-detecting) lifecycle; the admin-org LoginPolicy requirement gains an
  environment-specific `defaultRedirectUri`.

## Impact

- **cloud-provisioning**:
  - `src/zitadel/dynamic/smtp-activation.ts` — `read` becomes drift-detecting
    (query live activation state) instead of a pure no-op.
  - `src/zitadel/components/admin-org-config.ts` + `src/zitadel/index.ts` — pass
    the env-specific `consoleUrl`; drop / correct the dev fallback.
  - Prod `pulumi up` (with refresh) to remediate the live instance.
- **specification**: MODIFIED `identity-management` requirements (SMTP activation,
  admin-org login policy).
- Unblocks `organizer-accounts` 6.3 (operator passkey email delivery).
