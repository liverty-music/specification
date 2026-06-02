## Why

The self-hosted Zitadel Login UI v2 (`/ui/v2/login/*` at `auth.liverty-music.app`) currently renders with no product branding: a live check of the prod login screen shows no logo, default neutral colors (blue focus ring, gray buttons), and generic copy — it does not look like Liverty Music. The Zitadel instance has no label policy configured (`privateLabelingSetting: PRIVATE_LABELING_SETTING_UNSPECIFIED`, no `LabelPolicy`), so users authenticating into the product land on an unbranded, off-product screen. Applying Liverty Music's logo and brand colors is a low-risk, high-visibility trust/polish win that is fully declarative via the existing Pulumi Zitadel provider.

## What Changes

- Add a Zitadel **label policy** (branding) for the `liverty-music` product org so the hosted Login UI v2 displays Liverty Music **brand colors** instead of the default Zitadel appearance.
- **Enforce the branding per-application**: set the product `Project`'s `privateLabelingSetting` to `PRIVATE_LABELING_SETTING_ENFORCE_PROJECT_RESOURCE_OWNER_POLICY` (currently `UNSPECIFIED`) so the product app's login flow always renders the product org's branding regardless of the logging-in user's org. (Zitadel has no application-level label policy; the project's private-labeling setting is the per-application control that selects which org's branding applies.)
- Configure colors: primary/background/font/warn (and dark variants) derived from the existing frontend brand tokens, plus theme mode and `disableWatermark` (so any future Zitadel watermark is suppressed). Activate the policy so it takes effect.
- This is implemented in `cloud-provisioning` via the `@pulumiverse/zitadel` provider's native `LabelPolicy` resource + the `Project.privateLabelingSetting` field, wired into the existing Zitadel component graph; it ships through the normal Pulumi/ArgoCD flow.
- **Logo is explicitly deferred**: no Liverty Music logo asset exists yet, so this change applies colors/theme only. Adding the logo is a fast follow once an asset is available.

## Capabilities

### New Capabilities

<!-- none -->

### Modified Capabilities

- `identity-management`: add a requirement to configure Login UI branding (a Zitadel label policy with the Liverty Music logo and brand colors) for the product org, alongside the existing login-policy / OIDC-application provisioning.

## Impact

- **`cloud-provisioning` only** — no proto, backend, or frontend changes.
  - `src/zitadel/components/frontend.ts` (or a new sibling branding component): add a `zitadel.LabelPolicy` resource for the product org (colors/theme/watermark).
  - `src/zitadel/index.ts`: change the product `Project`'s `privateLabelingSetting` from `UNSPECIFIED` to `ENFORCE_PROJECT_RESOURCE_OWNER_POLICY`, and wire the label policy into the `Zitadel` orchestrator.
  - No logo asset required (logo deferred).
- Out of scope (deferred to separate future changes):
  - **Logo** — no asset yet.
  - **Login text/string customization** — Login UI v2 texts require the immature Settings V2 API.
- Supersedes the discarded Zitadel-Cloud-era WIP that attempted login-text overrides via the legacy Management API — obsolete after the self-hosted v4.x + Login UI v2 migration.
