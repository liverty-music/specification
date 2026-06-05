## Why

The Settings "About" section links to Terms of Service, Privacy Policy, and OSS Licenses, but all three point to `https://liverty.me/*` URLs that have no content. This is both a broken UX and a compliance gap: the app collects personal data (Zitadel account email/id, home area, follows, push subscriptions) and runs PostHog product analytics with cross-border transfer to PostHog Cloud EU — so a published Privacy Policy is mandatory under Japan's APPI (利用目的の公表 / 越境移転の情報提供) and is a hard requirement for App Store / Google Play submission (both require a reachable Privacy Policy URL). The OSS Licenses page is required by the attribution terms of the Apache-2.0 / MIT dependencies actually shipped in the bundle. Terms of Service, while not legally mandated, is practically required for an account-based service that surfaces third-party concert/ticket data (disclaimer of third-party-data accuracy).

## What Changes

- Add three in-app legal document pages reachable as real routes (not external links, not modal dialogs) so each has a stable URL — required for the App Store Connect / Play Console "Privacy Policy URL" field and for in-app reachability during review:
  - `/legal/terms` — Terms of Service
  - `/legal/privacy` — Privacy Policy
  - `/legal/licenses` — OSS Licenses
- Author full Japanese and English drafts of the Terms of Service and Privacy Policy, grounded in the actual data inventory (see Impact). Drafts are review-ready but SHALL be confirmed by a legal professional before public launch.
- Generate the OSS Licenses content automatically at build time from the production dependency tree (e.g. `license-checker` / `generate-license-file`), so it stays accurate without manual upkeep.
- Make the three legal routes reachable by guests / unauthenticated users (and by store reviewers), consistent with the route guard's existing early-guest Settings access.
- **MODIFIED**: the Settings About Section links change from external `liverty.me` URLs to the in-app routes.
- Carry the operating-entity details (trade name, contact email, governing law) as fill-in placeholders in the drafts; the individual-developer / trade-name stage values are supplied at implementation time.

## Capabilities

### New Capabilities
- `legal-documents`: In-app Terms of Service, Privacy Policy, and OSS Licenses pages — their routes, guest reachability, i18n (ja/en), required content sections, and the build-time auto-generation of the OSS license list.

### Modified Capabilities
- `settings`: The About Section requirement changes so its three links target the in-app `/legal/*` routes instead of external/webview URLs.

## Impact

- **Data inventory feeding the Privacy Policy** (verified from code): personal data — account email + user_id (Zitadel, self-hosted), `safe_address` (ERC-4337, derived from user id), home area, followed artists, language preference, push subscription / FCM device token, PostHog analytics events (cookies/localStorage). Third-party processors / transfers — **PostHog Cloud EU** (analytics, cross-border / APPI Art. 28), **Resend** (transactional email, US), **Google FCM / Web Push** (push, US), **Google Gemini / Vertex AI** (concert search, US), **Last.fm** (artist metadata, called from browser → IP exposure, UK). Zitadel is self-hosted on the project's own GKE, so it is not a third-party transfer.
- **Frontend code**: new `src/routes/legal/*` route components + templates, route registration in `app-shell.ts` with `data: { auth: false }`, i18n keys in `src/locales/{ja,en}/translation.json`, and the Settings About-section link targets in `settings-route.html`.
- **Build pipeline**: a license-extraction step that emits the OSS license list as a build artifact consumed by `/legal/licenses`.
- **Out of scope**: the GPL-in-zk-prover removal is tracked by the separate `remove-gpl-zk-prover` change; once it lands, the auto-generated OSS list will reflect the GPL-free dependency set. No GPL packages should remain by the time this page ships, but the generator is the source of truth regardless.
