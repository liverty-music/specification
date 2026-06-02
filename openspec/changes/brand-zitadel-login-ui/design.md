## Context

Zitadel is self-hosted (v4.14.0, Helm chart `zitadel/zitadel-charts@9.34.1`) with the new Login UI v2 (a separate Next.js container `zitadel-api-login`, served at `/ui/v2/login/*`). The instance is provisioned via Pulumi using `@pulumiverse/zitadel@^0.2.0` under `cloud-provisioning/src/zitadel/`, which manages an OIDC application, login policy, SMTP, actions, and a machine user for the `liverty-music` product org. No branding is configured today: `src/zitadel/index.ts` sets `privateLabelingSetting: PRIVATE_LABELING_SETTING_UNSPECIFIED` and there is no label policy. A live check of the prod login confirmed an unbranded screen (no logo, default colors).

Login UI v2 automatically honors the org/instance label policy, so branding is purely a provisioning concern — no changes to the login app, Helm chart, frontend, backend, or proto.

## Goals / Non-Goals

**Goals:**
- The hosted Login UI v2 shows Liverty Music brand colors for the product org, enforced for the product application's login flow.
- Declarative, IaC-managed, shipped through the existing Pulumi/ArgoCD flow; dev and prod parity.

**Non-Goals:**
- **Logo** — no Liverty Music logo asset exists yet; colors/theme only this change. Logo is a fast follow.
- Login text/string customization (Login UI v2 texts need the Settings V2 API; not provider-supported and immature — separate future change).
- Building/self-hosting a custom login app, or changing the Helm chart.
- Any frontend/backend/proto change.

## Decisions

- **Branding values live on an org-level `zitadel.LabelPolicy`; enforcement is per-application via the project.** Zitadel has **no application-level label policy** — branding is defined only at instance (`DefaultLabelPolicy`) or org (`LabelPolicy`) level. The per-application control is the **`Project.privateLabelingSetting`**, which selects *which* org's label policy the app's login flow renders. So:
  - Define a `LabelPolicy` on the `liverty-music` product org (the project's resource-owner org).
  - Set the product `Project.privateLabelingSetting` to `PRIVATE_LABELING_SETTING_ENFORCE_PROJECT_RESOURCE_OWNER_POLICY` (currently `UNSPECIFIED`) so the product app **always** renders the product org's branding, independent of the logging-in user's org.
  - This supersedes the existing defensive `UNSPECIFIED` (the old comment cited SMTP-conflict caution, which is unrelated to label policy); flip it deliberately and verify on dev.
  - Alternative considered: `DefaultLabelPolicy` (instance-level) — rejected; it would also brand the admin org's console login, which is intentionally separate.
  - Alternative considered: leaving `privateLabelingSetting: UNSPECIFIED` and relying on the org policy alone — rejected; enforcement is what guarantees the product app's login shows product branding regardless of the user's resource-owner org.
- **Reuse the frontend brand palette (colors only).** Frontend brand tokens (oklch) converted to the hex values Zitadel expects:

  | LabelPolicy field | Light | Dark | Source token |
  |---|---|---|---|
  | `primaryColor` / `primaryColorDark` | `#fd00a6` | `#fd00a6` | `--color-brand-primary` (pink) |
  | `backgroundColor` / `backgroundColorDark` | `#ffffff` | `#0d1023` | white / `--color-surface-base` |
  | `fontColor` / `fontColorDark` | `#161929` | `#fafafa` | dark navy / `--color-text-primary` |
  | `warnColor` / `warnColorDark` | `#f14d4c` | `#f14d4c` | `--color-error` |

  Also set `themeMode: THEME_MODE_AUTO` (follow the system; the v2 login exposes a toggle and both palettes are defined), `disableWatermark: true`, and `hideLoginNameSuffix: true` (cleaner consumer login name). Leave `logoUrl`/`logoPath` unset until an asset exists. Hex values are derived from the tokens and SHALL be visually confirmed on dev after apply.
- **Activate the policy.** Label policies are staged then activated in Zitadel; the resource must set it active (`setActive`) so the change is live.
- **Place the resource in the Zitadel component graph.** Add the `LabelPolicy` inside `FrontendComponent` (or a small dedicated branding component) and adjust `privateLabelingSetting` on the project in `src/zitadel/index.ts`.

## Risks / Trade-offs

- [Color-only branding without a logo] → A colors-only policy still meaningfully on-brands the login (brand-tinted buttons/links/background) without a logo. The logo slot simply stays empty, matching today's behavior. Acceptable; logo is a follow-up. → low.
- [Provider feature parity at v0.2.0] → Confirm `LabelPolicy` (colors + setActive) and `Project.privateLabelingSetting=ENFORCE_PROJECT_RESOURCE_OWNER_POLICY` work against self-hosted v4.14.0 via the pinned provider. Mitigation: verify on dev first.
- [Color accuracy] → Zitadel expects hex; the frontend tokens are oklch. Convert to the nearest hex and visually verify on dev.
- [Flipping privateLabelingSetting] → Changing it from `UNSPECIFIED` is a behavioral change to the login flow; verify on dev that console/admin login is unaffected (separate org) before prod.

## Open Questions

All blocking questions are resolved; the change is ready to implement.

- **Brand color hex** — resolved (table above; converted from frontend oklch tokens, to be visually confirmed on dev).
- **Admin/console org branding** — resolved: leave it as the Zitadel default. The admin/console org is intentionally separate; `ENFORCE_PROJECT_RESOURCE_OWNER_POLICY` is set only on the product project, so console login is untouched. No admin branding in this change.
- **`themeMode` / `hideLoginNameSuffix`** — resolved: `THEME_MODE_AUTO` + `hideLoginNameSuffix: true` (both palettes defined; adjustable after dev review).
- (Deferred, not blocking) **Logo asset** — file/URL and upload-vs-hosted-URL, for the follow-up logo change.
