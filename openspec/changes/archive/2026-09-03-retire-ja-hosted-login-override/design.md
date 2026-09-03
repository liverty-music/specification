## Context

The original change (`fix-zitadel-login-ja-i18n`) provisioned a **full** Japanese Hosted Login Translation override and a **full** English override (for a two-key "Liverty Music" rebrand), each pinned from upstream `apps/login/locales/*.json` at v4.14.0. Both were flagged "re-sync on Zitadel upgrades." Zitadel v4.17.0 now ships Japanese defaults, so the reason for the full Japanese override is gone.

## Merge semantics (why slimming is safe)

`internal/query/hosted_login_translation.go` at v4.17.1:

- `getSystemTranslation(lang, instanceDefaultLang)` returns `defaultSystemTranslations[lang]` (embedded `v2-default.json`), falling back to the instance default language only when `lang` is absent. `ja` is present from v4.17.0, so it returns real Japanese — not English.
- For an org-level request it loads the org (and instance) override, then `mergo.Merge(&override, systemTranslation)`. `mergo.Merge` fills only keys **missing** from the destination; existing override keys win.

Consequences:

- A **partial** override is complete at render time — absent keys back-fill from the system default of the same locale.
- The old "must stay complete or the API English-fills omitted keys" caveat was a v4.14.0 artifact (no `ja` default → fallback to English). It no longer holds.

Measured drift (pinned vs v4.17.1): `en` and `ja` each differ by one key (`idp.signInWithZitadel`); the `en` system default equals the login-bundle `en.json` (0 value diffs). So slimming changes no rendered string on v4.17.1.

## Decisions

- **Japanese: empty override, not resource removal.** Settings v2 exposes only `GetHostedLoginTranslation` / `SetHostedLoginTranslation` — no reset/delete — and the dynamic provider's `delete()` is intentionally a no-op (removing the Pulumi record must not wipe a live override). Removing the resource would therefore leave the stale full override in the DB. An **empty `Set`** upsert reliably neutralizes it: the override holds no keys, so `ja` resolves entirely to the system default and auto-tracks future versions. The (empty) resource is retained as the managed declaration of that neutralized state.
- **English: keep as a two-key partial override.** English is the instance default language, so the rebrand still needs an explicit override; but only `common.title` and `register.description` need pinning, with the rest back-filled from the system default.

## Alternatives considered

- **Leave both full overrides.** Rejected: perpetuates the per-upgrade re-sync burden and freezes strings at v4.14.0, drifting from the deployed version.
- **Delete the ja resource outright.** Rejected: the no-op `delete()` + missing reset RPC means the live override would persist unmanaged and frozen.
