## Why

The self-hosted Zitadel hosted Login UI v2 (`/ui/v2/login/*` at `auth.liverty-music.app`) renders the **Japanese** login screen in **English**, even though the instance allows Japanese and the user's language is Japanese. For a Japanese-first consumer product this is a visible, trust-eroding defect on the very first authenticated screen. The cause was confirmed end-to-end (live behavior + API responses + Zitadel source): Zitadel's backend default translations are missing Japanese, and that English fallback overrides the (complete) Japanese bundle. This is not fixable by configuration we already control, nor by upgrading Zitadel (latest `main` is still missing Japanese), so it needs a deliberate provisioning-side override.

## What Changes

- Provision a **Hosted Login Translation override for Japanese (`ja`)** on the `liverty-music` Zitadel deployment via the Settings v2 API (`SetHostedLoginTranslation`), so the hosted Login UI v2 renders Japanese text for `ja` users instead of falling back to English.
- The override carries the **complete** Japanese key set (sourced from Zitadel's own `apps/login/locales/ja.json`), because the API English-fills any key the override omits — a partial override would leave untranslated keys in English.
- Provision it declaratively through `cloud-provisioning` alongside the existing Zitadel resources, so it ships through the normal Pulumi/ArgoCD flow and survives instance rebuilds.
- File an **upstream Zitadel issue** to add the missing languages (`ja` plus `ar, cs, fr, hu, id, ko, mk, pt, ro, sv, tr, uk`) to `internal/query/v2-default.json`, tracking the permanent fix that would let the override be retired.

### Root cause (confirmed)

- Login v2 (`apps/login/src/i18n/request.ts`) computes messages as `deepmerge([en.json, <locale>.json, customMessages])`, where `customMessages = GetHostedLoginTranslation(locale)` is merged **last (wins)**.
- The frontend bundle `apps/login/locales/ja.json` is fully translated, but the backend default `internal/query/v2-default.json` contains only 8 languages (`de,en,es,it,nl,pl,ru,zh`) — **no `ja`**. So `GetHostedLoginTranslation(ja)` falls back to the instance default (`en`) and returns English, overriding the Japanese bundle.
- Evidence: `GetGeneralSettings` shows `allowedLanguages` includes `ja` and `defaultLanguage = en` (our config is correct); `GetHostedLoginTranslation` returns English for `ja` but German for `de`; the source `v2-default.json` has `de` but no `ja`; live `NEXT_LOCALE=de` → German, `NEXT_LOCALE=ja` → English. OIDC `ui_locales` is not consulted by login v2; the `accept-language` header and `NEXT_LOCALE` cookie ARE honored (proven via `de`).

### Out of scope

- The login middleware `fetch() returned undefined` / "Failed to load security settings for CSP" error (the middleware's API fetch omits the instance host header, so CSP falls back to default). Unrelated to localization — tracked separately.
- Login **logo** branding (no asset yet) — deferred, separate change.
- Other missing languages' overrides — this change ships Japanese only (the product's languages are JA/EN); the upstream issue covers the rest.

## Capabilities

### New Capabilities

<!-- none -->

### Modified Capabilities

- `identity-management`: add a requirement that the hosted Login UI v2 presents its interface text in Japanese for the product, provisioned via a Zitadel Hosted Login Translation override, since Zitadel's built-in defaults omit Japanese.

## Impact

- **`cloud-provisioning` only** — no proto, backend, or frontend changes.
  - Add a Zitadel Hosted Login Translation resource for `ja` (Settings v2 `SetHostedLoginTranslation`), provisioned in the Zitadel component graph. `@pulumiverse/zitadel` has no native resource for this, so it is implemented as a Pulumi **dynamic provider** (or equivalent seed) that calls the Settings v2 API with the `pulumi-admin` JWT — consistent with existing custom Zitadel automation under `src/zitadel/dynamic/`.
  - Carry the full `ja` translation payload (derived from upstream `apps/login/locales/ja.json`, pinned to the deployed Zitadel version `v4.14.0`).
- **Specification**: modify the `identity-management` capability spec (this change).
- **Upstream**: a Zitadel GitHub issue/PR to add the missing languages to `internal/query/v2-default.json` (permanent fix; lets this override be removed later).
- Ships through the normal Pulumi/ArgoCD flow; prod parity; visually verified on prod (JA login renders Japanese in light + dark).
