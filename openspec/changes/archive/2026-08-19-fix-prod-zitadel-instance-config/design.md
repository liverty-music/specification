## Context

Two prod Zitadel instance-config defects (see proposal.md), both in
`cloud-provisioning/src/zitadel`. Diagnosis done live: prod Postmark server
(`Liverty Music [prod]`, id 18504491) shows **0 sends** with a verified sending
domain and a valid server token, and `auth.liverty-music.app/ui/login/`
302-redirects to `https://auth.dev.liverty-music.app/ui/console`. The Pulumi
resources exist (`SmtpConfig` + `ZitadelSmtpActivation`, `AdminOrgConfigComponent`)
— these are runtime-state / wiring defects, not missing resources.

## Goals / Non-Goals

**Goals:** SMTP activation that self-heals runtime drift; a `defaultRedirectUri`
that always points at the environment's own console; remediate the live prod
instance so email delivers and the console stops redirecting to dev.

**Non-Goals:** Postmark account/DNS changes (prod server + `mail.liverty-music.app`
already verified), new email templates, any organizer-domain code.

## Decisions

**D1 — Self-healing SMTP activation via a drift-detecting `read`.**
`ZitadelSmtpActivation` (`src/zitadel/dynamic/smtp-activation.ts`) currently has a
no-op `read`, so once the live config drifts inactive Pulumi never notices. Change
`read` to call `POST /admin/v1/smtp/_search` (the same discovery the `create`
handler already does) and inspect the config's `state`:
- If the config is missing or **not** `SMTP_CONFIG_ACTIVE`, return props that
  differ from the recorded state (e.g. drop/blank `activatedAt`, or surface a
  `state` field) so Pulumi reports drift on `refresh` and the subsequent `up`
  re-runs activation.
- If it is `SMTP_CONFIG_ACTIVE`, return the recorded state unchanged (steady-state
  no redundant `_activate`).
Re-activation itself reuses the existing idempotent `_activate` call (2xx or
"already active" = success). Healing requires a **refreshing** `up`
(`pulumi up --refresh`, or the prod Pulumi Cloud deployment configured to
refresh); document that in the runbook/tasks. Keep `delete` a no-op (removing the
Pulumi record must not deactivate live SMTP). This trades the previous
"zero-HTTP steady state" for one lightweight `_search` per refresh — an
acceptable cost for eliminating a silent-outage class.

**D2 — Pass the environment-specific `consoleUrl`.**
`AdminOrgConfigComponent` already accepts a `consoleUrl` arg and applies it as the
admin-org LoginPolicy `defaultRedirectUri`, but defaults to a hardcoded
`https://auth.dev.liverty-music.app/ui/console` and the call site
(`src/zitadel/index.ts`) never passes it. Pass
`consoleUrl: pulumi.interpolate\`https://${domain}/ui/console\`` (the same
per-env `domain` the component already receives for the Zitadel host) at the call
site. Remove the dev-pointing fallback, or make it the current-env domain, so no
environment can silently inherit another's console. Dev is unaffected in value
(its `domain` already resolves to `auth.dev.liverty-music.app`).

**D3 — Remediation ordering.** After merge, a refreshing prod `pulumi up`:
(1) `read`/refresh detects the drifted SMTP → `_activate` re-runs → active;
(2) the admin-org LoginPolicy `defaultRedirectUri` updates to the prod console.
Confirm the prod Postmark server records a delivered email and
`auth.liverty-music.app/ui/login/` no longer redirects to dev. Rotate the prod
Postmark Server API Token afterward (it was shared in plaintext during
diagnosis) and update ESC.

## Risks / Trade-offs

- **`read` now issues an API call on refresh** → one `_search` per refresh; bounded
  and only on refreshing applies. Worth it to remove the silent-outage failure mode.
- **Refresh dependency** → self-healing only triggers on a refreshing `up`; if the
  prod deployment does not refresh, drift persists. Mitigation: enable refresh on
  the prod deployment (or run `pulumi up --refresh`) — captured in tasks.
- **Multiple SMTP configs** → `_search` assumes exactly one config per instance
  (the existing `create` handler already asserts this); preserve that assumption
  and its explicit error.

## Migration Plan

1. cloud-provisioning: implement D1 (`smtp-activation.ts` `read`) + D2
   (`admin-org-config.ts` fallback + `index.ts` call site); `make lint-ts`.
2. Merge → refreshing prod `pulumi up` (manual, Pulumi Cloud console).
3. Verify: prod Postmark shows a delivered email; prod console no longer
   redirects to dev; then finish `organizer-accounts` 6.3.
4. Rotate the prod Postmark token; update ESC.
- Rollback: both changes are additive/wiring — revert restores the prior
  (broken) behavior; no data migration.

## Open Questions

- Whether to also enable refresh on the prod Pulumi Cloud deployment permanently
  (so future SMTP drift self-heals on the next scheduled apply) vs. relying on
  operators to pass `--refresh` — resolved in tasks as "enable refresh on the
  prod deployment" if the console supports it, else document the `--refresh`
  requirement in the runbook.
