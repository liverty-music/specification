## 1. Branding inputs (resolved — see design.md palette table)

- [x] 1.1 Brand color hex values derived from frontend tokens: primary `#fd00a6`; background light `#ffffff` / dark `#0d1023`; font light `#161929` / dark `#fafafa`; warn `#f14d4c`. `themeMode: THEME_MODE_AUTO`, `disableWatermark: true`, `hideLoginNameSuffix: true`. No logo (deferred).

## 2. Provision the label policy + per-app enforcement

- [x] 2.1 Add a `zitadel.LabelPolicy` resource (in `src/zitadel/components/frontend.ts` or a new branding component) for the `liverty-music` product org with the brand colors, `themeMode`, `disableWatermark: true`, and `setActive: true`. Leave `logoUrl`/`logoPath` unset.
- [x] 2.2 In `src/zitadel/index.ts`, change the product `Project`'s `privateLabelingSetting` from `PRIVATE_LABELING_SETTING_UNSPECIFIED` to `PRIVATE_LABELING_SETTING_ENFORCE_PROJECT_RESOURCE_OWNER_POLICY`, and wire the label policy into the `Zitadel` orchestrator.
- [x] 2.3 Run `pulumi preview` and confirm only the expected `LabelPolicy` add + `privateLabelingSetting` update appear (no unintended resource churn). Verified via Pulumi Cloud prod preview on PR #347: `brand` LabelPolicy create + `liverty-music` Project update, exactly as designed. (One unrelated pre-existing cosmetic drift on `dashboard-zitadel-observability` — not introduced by this change.)

## 3. Ship and verify on prod

- [x] 3.1 Apply through the normal release/ArgoCD flow. Merged PR #347 → dev auto-applied (no-op: dev Zitadel dormant); prod applied via Pulumi Cloud (`create:1` LabelPolicy + `update:2`). NOTE: Login UI v2 caches branding — a `kubectl rollout restart deploy/zitadel-api-login -n zitadel` was required for the new policy to render.
- [x] 3.2 Open `https://auth.liverty-music.app/ui/v2/login/*` through the product OIDC flow and confirm the login shows the Liverty Music brand colors in both light and dark mode, with no Zitadel default colors/watermark. Verified: primary `#fd00a6`, bg `#ffffff`/`#0d1023`, font `#161929`/`#fafafa`, warn `#f14d4c`; pink Continue button + focus ring in both themes; no watermark. (themeMode AUTO follows system.)
- [x] 3.3 Confirm the admin/console login is unaffected by the `privateLabelingSetting` change (separate org). Verified: `/ui/console` login still renders Zitadel defaults (primary `#5469d4`/`#2073c4`, no pink).
