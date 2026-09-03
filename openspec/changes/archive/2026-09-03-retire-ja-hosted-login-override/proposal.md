## Why

The `identity-management` capability requires the product to provision a **full Japanese Hosted Login Translation override** for the hosted Login UI v2, because Zitadel's backend hosted-login defaults (`internal/query/v2-default.json`) omitted Japanese — so the Settings API returned English for `ja` and that English overrode the login app's bundled Japanese.

That gap is now fixed upstream. **Zitadel v4.17.0 ships Japanese** in `v2-default.json` (prod runs v4.17.1, upgraded 2026-08-23), and the query merges any org override **over** the system default, back-filling absent keys from the system default of the requested locale (confirmed in `internal/query/hosted_login_translation.go`). So the pinned full Japanese override is now redundant, and — because it is frozen at the payload pinned from v4.14.0 — it is a standing maintenance item that must be hand-re-synced on every upgrade.

The requirement should be updated to (a) rely on the upstream Japanese defaults, (b) retire the pinned Japanese override, and (c) keep only the minimal English override that carries the product "Liverty Music" rebrand.

## What Changes

- **Rely on upstream defaults for Japanese.** Stop provisioning a Japanese Hosted Login Translation override that carries a pinned Japanese key set. Japanese now renders from Zitadel's built-in defaults (v4.17.0+).
- **Neutralize the historical Japanese override with an empty upsert.** Zitadel's Settings v2 API exposes only `Get`/`Set` for hosted-login translations — there is **no reset/delete RPC** — and the `cloud-provisioning` dynamic provider's `delete()` is a no-op. Removing the provisioning resource would therefore strand the stale full override in the DB. Setting an **empty** payload via `SetHostedLoginTranslation` neutralizes it: the override contributes no keys, leaving `ja` served entirely by the upstream default.
- **Slim the English override to the rebrand keys only.** The English override exists solely to replace "Zitadel" with "Liverty Music" in the login title and register description. Because a partial override back-fills every other key from the running version's English default, it is reduced to just those two keys — no more pinned full `en.json` to re-sync per upgrade.

## Capabilities

### New Capabilities

<!-- none -->

### Modified Capabilities

- `identity-management`: the "Localize Login UI Text for the Product" requirement is modified — Japanese is served by Zitadel's upstream hosted-login defaults (v4.17.0+) with the historical override neutralized, and only a minimal English rebrand override remains.

## Impact

- **`cloud-provisioning` only** — no proto, backend, or frontend changes. Implemented in `cloud-provisioning` PR (`optimize-hosted-login-translation-overrides`): `ja` override emptied, `en` override reduced to the two rebrand keys, vendored `src/zitadel/translations/{en,ja}.json` and their biome ignore removed.
- **Provisioning**: applied through the normal Pulumi/ArgoCD flow. `pulumi up` is manual for prod (repo protocol). After apply, a `zitadel-api-login` pod restart may be needed to clear the login container's translation cache.
- **Behavior**: no user-visible change expected on v4.17.1 — the English system default equals the login image's bundled `en.json` (0 value diffs), and the emptied Japanese override resolves to a system default that matches the retired payload.
- **Upstream**: closes the loop on the tracking issue (zitadel/zitadel #12230), which is resolved as of v4.17.0.
