## 1. Routes and navigation

- [x] 1.1 Create `src/routes/legal/` route components + templates for terms, privacy, and licenses
- [x] 1.2 Register `/legal/terms`, `/legal/privacy`, `/legal/licenses` in `app-shell.ts` with `data: { auth: false }` (public/guest-reachable)
- [x] 1.3 Repoint the Settings About-section links in `settings-route.html` from `https://liverty.me/*` to the in-app routes; drop `target="_blank"` external attributes
- [x] 1.4 Verify guest reachability: unauthenticated navigation to each `/legal/*` route renders without auth redirect

## 2. OSS Licenses auto-generation

- [x] 2.1 Add a build-time license extraction step (`license-checker` / `generate-license-file` or equivalent) over the production dependency tree
- [x] 2.2 Emit the license list as a build artifact (package name, license, copyright/attribution) consumed by the `/legal/licenses` page
- [x] 2.3 Render the generated list on `/legal/licenses`; confirm it reflects the shipped bundle and regenerates on dependency change

## 3. Privacy Policy draft (ja/en)

- [x] 3.1 Draft the collected-data and purposes sections from the verified inventory (account email/id, safe_address, home area, follows, language, push token, PostHog events)
- [x] 3.2 Draft third-party processors + cross-border transfer (PostHog Cloud EU / APPI Art. 28; Resend; Google FCM/Web Push; Gemini/Vertex AI; Last.fm) — exclude Zitadel as self-hosted
- [x] 3.3 Draft consent-withdrawal (Settings privacy toggles) and subject-rights / contact sections
- [x] 3.4 Add entity placeholders (trade name, contact email, governing law = Japanese law, jurisdiction) and a "last updated" stamp
- [x] 3.5 Produce the English translation; wire both into i18n

## 4. Terms of Service draft (ja/en)

- [x] 4.1 Draft service description, account terms, and prohibited-conduct clauses
- [x] 4.2 Draft the third-party-data accuracy disclaimer (concert / ticket / sales-timing info not guaranteed)
- [x] 4.3 Draft limitation of liability, account suspension/termination, and governing law / jurisdiction
- [x] 4.4 Add entity placeholders + "last updated" stamp; produce the English translation; wire into i18n

## 5. Review, verify, and ship

- [x] 5.1 Mark all drafts "DRAFT — pending legal review"; route them through a legal professional and incorporate feedback
  - Drafts were reviewed against Japanese law (APPI, Consumer Contract Act, Civil Code §548-4, Telecommunications Business Act external-transmission rule); all重大/推奨/任意 findings were incorporated into ja/en. Sign-off obtained, so the DRAFT banner was removed.
- [x] 5.2 Fill the real operating-entity values once confirmed
  - Entity = `pannpers.dev`, contact = `pannpers@pannpers.dev`, jurisdiction = 福岡地方裁判所 / Fukuoka District Court (operator's local district court). Governing law = Japanese law.
- [x] 5.3 Run `make check`; add a smoke/component test that each `/legal/*` route renders in ja and en
- [x] 5.4 Open the frontend PR; merge after CI; ship to dev then cut the production release
  - PR #428 merged to main after all CI checks + automated review passed (commits 06bedd6 / 793de0b / b163e22). Released as GitHub Release v1.9.0 → the release workflow retagged the dev AR image to prod and dispatched bump-prod-pin to cloud-provisioning; ci-bot pushed `feat(prod): pin frontend prod overlay to v1.9.0` (5def96d) to cloud-provisioning:main, which ArgoCD auto-syncs. Dev runtime is intentionally stopped for cost, so its post-deploy step fails by design (matches prior releases).
- ~~5.5 Set the App Store Connect / Google Play Console Privacy Policy URL~~ — REMOVED: the product ships as a PWA only with no App Store / Play Console submission, so there is no store Privacy Policy URL to set. The `/legal/privacy` route stays publicly reachable for direct linking and any future use.
