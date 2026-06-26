# Tasks — Disclose PostHog in the in-app Privacy Policy

## 1. Privacy Policy content (APPI Article 28 disclosure)

- [x] 1.1 Update the English Privacy Policy content (`frontend/src/locales/en/translation.json`, under `legal.privacy.sections`) so the cross-border / third-party sections name PostHog as operated by Klant Solutions B.V., Netherlands, as a named cross-border recipient under APPI Article 28.
- [x] 1.2 In the English content, enumerate the categories of data transferred to PostHog (interaction / usage events captured via cookies and localStorage) and the purpose (product analytics: improving the Service and measuring effectiveness) in the data-category / external-transmission listing.
- [x] 1.3 Mirror 1.1 and 1.2 in the Japanese Privacy Policy content (`frontend/src/locales/ja/translation.json`), keeping ja as the authoritative legal locale and the section structure parallel to en.
- [x] 1.4 Bump `legal.privacy.lastUpdated` in both en and ja.

## 2. Fix broken legal links

- [x] 2.1 In `frontend/src/routes/consent/consent-route.html` (the `https://liverty.me/privacy` anchor at ~line 35), route the link through in-app navigation to the `/legal/privacy` route instead of the dead external URL (drop the external `target="_blank"` / `rel="noopener noreferrer"` treatment), using the route's existing in-app navigation mechanism.
- [x] 2.2 In `frontend/src/routes/settings/settings-route.html`, reconcile / dedupe the two Privacy Policy links: the ABOUT-section row at ~line 230 already calls `openLegal('/legal/privacy')` correctly, while the analytics opt-out anchor at ~line 201 still points at the dead `https://liverty.me/privacy`. Route the broken one through the existing `openLegal('/legal/privacy')` mechanism (do NOT introduce a second external link), and reconcile the two so there is a single consistent in-app navigation path; drop the external-link treatment on the fixed anchor. Confirm whether both links are still warranted or whether the analytics-section reference can simply reuse/point to the same handler.

## 3. Verify

- [x] 3.1 Run `make lint` in `frontend/` and fix any lint / format / typecheck issues.
- [x] 3.2 Run the frontend build (`npm run build`) and confirm it succeeds; manually verify the consent and settings links navigate to `/legal/privacy`.

## 4. Review

- [x] 4.1 Policy owner reviewed and signed off on the legal copy (en + ja) for release. For this individual-operator service the operator is the policy owner; no external legal counsel review is engaged.
- [x] 4.2 Policy owner confirmed the PostHog (Klant Solutions B.V.) classification as *processor acting on Liverty's behalf* (entrustment of handling), not an independent third-party recipient — the cross-border copy was finalized accordingly (en/ja section 6).
