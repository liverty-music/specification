## 1. Routes and navigation

- [ ] 1.1 Create `src/routes/legal/` route components + templates for terms, privacy, and licenses
- [ ] 1.2 Register `/legal/terms`, `/legal/privacy`, `/legal/licenses` in `app-shell.ts` with `data: { auth: false }` (public/guest-reachable)
- [ ] 1.3 Repoint the Settings About-section links in `settings-route.html` from `https://liverty.me/*` to the in-app routes; drop `target="_blank"` external attributes
- [ ] 1.4 Verify guest reachability: unauthenticated navigation to each `/legal/*` route renders without auth redirect

## 2. OSS Licenses auto-generation

- [ ] 2.1 Add a build-time license extraction step (`license-checker` / `generate-license-file` or equivalent) over the production dependency tree
- [ ] 2.2 Emit the license list as a build artifact (package name, license, copyright/attribution) consumed by the `/legal/licenses` page
- [ ] 2.3 Render the generated list on `/legal/licenses`; confirm it reflects the shipped bundle and regenerates on dependency change

## 3. Privacy Policy draft (ja/en)

- [ ] 3.1 Draft the collected-data and purposes sections from the verified inventory (account email/id, safe_address, home area, follows, language, push token, PostHog events)
- [ ] 3.2 Draft third-party processors + cross-border transfer (PostHog Cloud EU / APPI Art. 28; Resend; Google FCM/Web Push; Gemini/Vertex AI; Last.fm) — exclude Zitadel as self-hosted
- [ ] 3.3 Draft consent-withdrawal (Settings privacy toggles) and subject-rights / contact sections
- [ ] 3.4 Add entity placeholders (trade name, contact email, governing law = Japanese law, jurisdiction) and a "last updated" stamp
- [ ] 3.5 Produce the English translation; wire both into i18n

## 4. Terms of Service draft (ja/en)

- [ ] 4.1 Draft service description, account terms, and prohibited-conduct clauses
- [ ] 4.2 Draft the third-party-data accuracy disclaimer (concert / ticket / sales-timing info not guaranteed)
- [ ] 4.3 Draft limitation of liability, account suspension/termination, and governing law / jurisdiction
- [ ] 4.4 Add entity placeholders + "last updated" stamp; produce the English translation; wire into i18n

## 5. Review, verify, and ship

- [ ] 5.1 Mark all drafts "DRAFT — pending legal review"; route them through a legal professional and incorporate feedback
- [ ] 5.2 Fill the real operating-entity values once confirmed
- [ ] 5.3 Run `make check`; add a smoke/component test that each `/legal/*` route renders in ja and en
- [ ] 5.4 Open the frontend PR; merge after CI; ship to dev then cut the production release
- [ ] 5.5 Set the App Store Connect / Google Play Console Privacy Policy URL to the production `/legal/privacy` URL
