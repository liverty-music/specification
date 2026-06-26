# Disclose PostHog in the in-app Privacy Policy

## Why

PostHog product analytics is now live and transfers usage data to PostHog Cloud EU, operated by Klant Solutions B.V. in the Netherlands. This is a cross-border transfer of usage data to a recipient in a foreign country, which carries a disclosure obligation (APPI Article 28 is the likely basis; the exact characterization — processor vs. independent recipient — is for counsel to confirm): the privacy policy should name the recipient and its country and enumerate the data categories transferred and the purpose of the transfer.

The archived `introduce-analytics-tool` change marked tasks 11.1 and 11.2 as `[~]` EXTERNAL, on the assumption that the privacy policy lived off-repo at `https://liverty.me/privacy`. That assumption is wrong: `liverty.me` does not exist, and the Privacy Policy is an in-app route (`/legal/privacy`) rendered by the `legal-document` component from the i18n resource bundle. So the obligation was never actually discharged, and the in-app consent notice and settings link to a dead URL.

This change discharges the APPI Article 28 disclosure in the place it actually lives — the in-app Privacy Policy content — and fixes the two broken external links to point at the real in-app route. It completes 11.1/11.2 and makes the `analytics-consent` capability's "Purpose of use is published rather than gated" requirement true in fact, not just in intent.

## What Changes

- Update the in-app Privacy Policy i18n content (`frontend/src/locales/{en,ja}/translation.json`, under `legal.privacy.sections`) so it explicitly names PostHog (operated by Klant Solutions B.V., Netherlands) as a cross-border recipient of usage analytics data, and enumerates the recipient's country, the categories of data transferred, and the purpose of the transfer. (Whether the wording legally suffices under APPI Article 28, and whether PostHog is a processor or an independent recipient, is confirmed by the policy owner / counsel — see design.md Open Questions.)
- Fix a bug: the onboarding consent notice (`frontend/src/routes/consent/consent-route.html`, dead anchor ~line 35) and the analytics opt-out anchor in the settings page (`frontend/src/routes/settings/settings-route.html`, ~line 201) link to the non-existent `https://liverty.me/privacy`. The settings ABOUT-section link (~line 230) already navigates in-app via `openLegal('/legal/privacy')`; reconcile / dedupe the broken anchor to reuse that same in-app mechanism rather than adding a second link, and re-point the consent anchor at the in-app `/legal/privacy` route.
- No backend, proto, or schema changes; this is frontend content plus a link fix.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `legal-documents` — the Privacy Policy disclosure requirement is strengthened to mandate naming third-party cross-border recipients (incl. PostHog / Klant Solutions B.V.) with the recipient's country (NL), the transferred data categories, and the purpose; the legal-sufficiency judgement under APPI Article 28 is left to counsel rather than encoded as normative spec text. A new requirement mandates that in-app legal links resolve to the in-app legal routes rather than external or broken domains.

## Impact

- Affected specs: `legal-documents`.
- Affected code:
  - `frontend/src/locales/en/translation.json`, `frontend/src/locales/ja/translation.json` (Privacy Policy content)
  - `frontend/src/routes/consent/consent-route.html` (broken link)
  - `frontend/src/routes/settings/settings-route.html` (broken link)
- Discharges a live APPI Article 28 disclosure obligation. The legal copy SHALL be reviewed by the policy owner before release.
