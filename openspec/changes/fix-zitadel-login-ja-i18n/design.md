## Context

Zitadel is self-hosted (v4.14.0) with the Login UI v2 (`zitadel-api-login` Next.js container, served at `/ui/v2/login/*`), provisioned via Pulumi under `cloud-provisioning/src/zitadel/`. The hosted login renders the Japanese screen in English. Root cause, confirmed end-to-end:

- `apps/login/src/i18n/request.ts` resolves the locale from the `accept-language` header / `NEXT_LOCALE` cookie (OIDC `ui_locales` is NOT used), gated by `allowedLanguages` from `GetGeneralSettings`. It then renders `deepmerge([en.json, <locale>.json, GetHostedLoginTranslation(locale)])` — the API translation is merged **last and wins**.
- The frontend bundle `apps/login/locales/ja.json` is complete Japanese, but the backend default `internal/query/v2-default.json` ships only `de,en,es,it,nl,pl,ru,zh` — **no `ja`**. So `GetHostedLoginTranslation(ja)` falls back to the instance default (`en`) and returns English, which overrides the Japanese bundle. `de` works because `v2-default.json` includes it.
- Verified: `GetGeneralSettings` → `allowedLanguages` includes `ja`, `defaultLanguage = en` (our config is correct); `GetHostedLoginTranslation(ja)` → English, `(de)` → German; `v2-default.json` has `de` (`"Ein weiteres Konto hinzufügen"`, matching the API) and no `ja`; live `NEXT_LOCALE=de` → German, `=ja` → English. `main` (latest) still omits `ja`, so a version bump does not fix it.

The existing Zitadel component graph already includes custom automation that calls Zitadel APIs with the `pulumi-admin` JWT via Pulumi dynamic providers under `src/zitadel/dynamic/` (e.g. user-IdP-link, permanent-password). The Settings v2 API exposes `SetHostedLoginTranslation` (instance or org level), which merges the supplied keys over the system defaults and accepts any supported BCP 47 locale (incl. `ja`).

## Goals / Non-Goals

**Goals:**
- The hosted Login UI v2 presents Japanese interface text for `ja` users of the product login flow, instead of falling back to English.
- Declarative, IaC-managed, shipped through the existing Pulumi/ArgoCD flow; survives instance rebuilds; dev/prod parity; verified on prod.
- Track the permanent upstream fix so the override can be retired.

**Non-Goals:**
- Fixing the unrelated middleware CSP `fetch() returned undefined` error (separate instance-host-header issue).
- Overriding languages other than Japanese (product is JA/EN; the rest are covered by the upstream issue).
- Any frontend/backend/proto change, login logo, or login behavior change.

## Decisions

- **Override Japanese via a Hosted Login Translation, provisioned as a Pulumi dynamic resource.** `@pulumiverse/zitadel` has no native resource for hosted-login translations, so implement a dynamic provider (mirroring `src/zitadel/dynamic/`) that calls Settings v2 `SetHostedLoginTranslation` with the `pulumi-admin` JWT. Provisioning it in IaC (vs a one-off API call) makes it reviewable, repeatable, and durable across instance rebuilds.
  - **Level: product org (`liverty-music`).** Set the translation at the product-org level so it scopes to product end-user logins and does not alter the admin/console org. (Instance level is the alternative; org level is the narrower, product-aligned blast radius. Either renders Japanese for `ja` viewers; org level is preferred.)
- **Ship the COMPLETE `ja` key set.** The API English-fills any key the override omits, and that English then wins the `deepmerge` over the bundled `ja.json`. A partial override would leave the un-supplied keys in English. Source the payload from upstream `apps/login/locales/ja.json` **pinned to the deployed Zitadel version (`v4.14.0`)** so keys line up with what the running login app expects.
- **Branding cache caveat.** The Login UI v2 caches translation/branding; after applying, the change may require a `kubectl rollout restart deploy/zitadel-api-login` to render (same operational pattern observed for the label-policy branding rollout). Capture this in tasks/verification.
- **Permanent fix is upstream.** File a Zitadel issue (and ideally a PR) to add `ja` (and the other missing languages) to `internal/query/v2-default.json`. Once a Zitadel release ships Japanese defaults, this override becomes redundant and can be removed — note this exit condition in the change.

## Risks / Trade-offs

- [Translation drift vs upstream] The override duplicates upstream's `ja.json`. If Zitadel renames/adds keys in a later login version, the pinned payload can go stale (new keys would fall back to English). → Mitigation: pin the payload to the deployed Zitadel version and re-sync on Zitadel upgrades; the upstream fix removes the duplication entirely. → low/medium.
- [Settings v2 API surface via dynamic provider] `SetHostedLoginTranslation` must work against self-hosted v4.14.0 with the `pulumi-admin` JWT at org level. → Mitigation: the same JWT already drives other Settings/Management calls in `src/zitadel/dynamic/`; verify on prod (dev Zitadel is currently stopped). → low.
- [Cache masking the result] Post-apply the login may keep serving cached English until the login pod is restarted. → Mitigation: include a rollout-restart + re-verify step; do not conclude failure before restart. → low.
- [Blast radius] Org-level override only affects product `ja` logins (currently English); it cannot regress en/de/other users or auth logic. → low.
