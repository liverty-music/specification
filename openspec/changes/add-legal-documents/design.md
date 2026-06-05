## Context

Settings → 情報 (About) shows three rows — 利用規約 / プライバシーポリシー / OSSライセンス — all linking to empty `https://liverty.me/*` pages. The app is a guest-capable Aurelia 2 PWA with ja/en i18n already wired (`src/locales/{ja,en}/translation.json`, `settings.termsOfService` etc.). The route guard (`AuthHook`) already grants unauthenticated users early access to Settings, and public routes opt out via `data: { auth: false }`.

The Privacy Policy is the load-bearing document: the app runs PostHog analytics with cross-border transfer to PostHog Cloud EU, which the consent layer already models against APPI Art. 28. The operating entity is at the individual-developer / trade-name stage, so concrete entity values (trade name, contact email) are fill-ins, not blockers — an individual is a valid 個人情報取扱事業者.

## Goals / Non-Goals

**Goals:**
- Give each legal document a stable in-app URL reachable by guests and store reviewers.
- Produce review-ready full ja/en drafts of Terms and Privacy grounded in the real data inventory.
- Keep the OSS Licenses list accurate automatically via build-time generation.
- Scope the Privacy Policy to Japan/APPI; structure it so EU/GDPR clauses can be added later without a rewrite.

**Non-Goals:**
- GDPR compliance now — not required unless the service targets EU residents; PostHog Cloud EU is a processor location, not a GDPR trigger.
- Standalone marketing site at `liverty.me` — in-app routes are the source of truth; a future external site can 301 to them.
- Final legal sign-off — drafts are a starting point requiring professional review before launch.
- Tokushōhō (特定商取引法) address disclosure — not required while there is no paid offering; a contact email suffices.

## Decisions

### Decision 1: In-app routes, not modal dialogs

**Choice:** Render each document at a real route (`/legal/terms`, `/legal/privacy`, `/legal/licenses`).

**Rationale:** App Store Connect and Google Play Console both require a reachable Privacy Policy **URL**; a modal/bottom-sheet has no URL and fails submission. Routes are also shareable and deep-linkable. The dialog idea (raised earlier) is fine for ephemeral content but cannot satisfy the store URL requirement, so it is rejected for these documents.

**Alternatives considered:** External `liverty.me` pages (rejected: needs separate hosting + its own i18n, and duplicates content); modal dialog (rejected: no URL).

### Decision 2: Guest-reachable public routes

**Choice:** Register the `/legal/*` routes with `data: { auth: false }` so unauthenticated users and store reviewers can open them directly.

**Rationale:** Store review happens without an account; legal docs must be reachable pre-auth. Consistent with the route guard's existing early-Settings access for guests.

### Decision 3: Author Terms + Privacy as full drafts; auto-generate OSS Licenses

**Choice:** Hand-author full ja/en drafts for Terms and Privacy from the verified data inventory. Generate the OSS Licenses page content at build time from the production dependency tree (`license-checker` or equivalent) into an artifact consumed by `/legal/licenses`.

**Rationale:** Terms/Privacy require human judgment and entity specifics; OSS attribution is mechanical and rot-prone if hand-maintained. Auto-generation also doubles as a license audit (it surfaced the GPL issue in the first place).

### Decision 4: Privacy Policy content contract (from the real inventory)

The Privacy Policy SHALL enumerate, accurately:
- **Collected data:** account email + user id (Zitadel, self-hosted), `safe_address`, home area, followed artists, language preference, push subscription / FCM token, PostHog events (cookies/localStorage).
- **Purposes:** service provision; usage analysis (improvement); ad-effectiveness measurement; push delivery.
- **Third-party processors / transfers:** PostHog Cloud EU (analytics; cross-border, APPI Art. 28), Resend (email, US), Google FCM/Web Push (push, US), Google Gemini/Vertex AI (concert search, US), Last.fm (artist metadata; browser-direct, IP exposure, UK). Zitadel is self-hosted → not a transfer.
- **Consent withdrawal:** the Settings "使い心地の改善" / "広告効果の測定" toggles.
- **Subject rights / contact:** disclosure / correction / deletion request channel = contact email.

### Decision 5: Entity values as placeholders

**Choice:** Drafts use clearly-marked placeholders (`<!-- 事業者名 -->`, `<!-- 連絡先メール -->`, governing law = Japanese law, jurisdiction = entity's district court). Implementation fills the real values.

**Rationale:** Unblocks drafting and review structure without waiting on entity finalization.

## Risks / Trade-offs

- **Drafts mistaken for final legal text** → Mitigation: mark every draft "DRAFT — pending legal review" and gate launch on professional sign-off.
- **Data inventory drifts as features change** (new SDK/processor added later) → Mitigation: the Privacy Policy's processor list must be revisited whenever a third-party integration is added; note this in the spec.
- **OSS generator output churns the page on every dep bump** → Mitigation: generate at build time into a versioned artifact; the page reflects the shipped bundle, which is correct behavior.
- **Auto-generated OSS list could still show GPL until `remove-gpl-zk-prover` lands** → Mitigation: the generator is the source of truth; if shipped before that change, the page truthfully lists GPL — acceptable transitional state, resolved when the prover swap merges.

## Migration Plan

1. Add `/legal/*` routes (public) + minimal page shells; repoint Settings About links.
2. Land the OSS license generator + wire `/legal/licenses`.
3. Author ja/en Terms + Privacy drafts; fill entity placeholders.
4. Legal review pass; incorporate feedback.
5. Ship to dev, then production release; update App Store Connect / Play Console Privacy Policy URL to `/legal/privacy`.
6. **Rollback:** revert the Settings link targets to the prior external URLs; routes are additive and can be removed without side effects.

## Open Questions

- Final operating-entity values (trade name, contact email, jurisdiction) — supplied at implementation.
- Whether to add a lightweight "last updated" date + version stamp per document (recommended for Privacy Policy change tracking).
