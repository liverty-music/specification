# Design — Disclose PostHog in the in-app Privacy Policy

## Context

The Privacy Policy is an in-app route at `/legal/privacy`, rendered by the `legal-document` Aurelia 2 component (`frontend/src/components/legal-document/`). The component reads its content from the i18n resource bundle: it resolves `legal.privacy.title`, `legal.privacy.intro`, `legal.privacy.lastUpdated`, and a variable-length `legal.privacy.sections[]` array (each `{ heading, body[] }`) via `@aurelia/i18n` with `returnObjects: true`. Content therefore lives entirely in `frontend/src/locales/{en,ja}/translation.json` and follows the active locale, with Japanese as the primary legal locale.

The archived `introduce-analytics-tool` change discharged the in-app consent/settings UI (FE PR #465) but deferred the policy-page edit (tasks 11.1/11.2) as "EXTERNAL", believing the policy lived at `https://liverty.me/privacy`. That domain does not exist. The consent notice and settings screen both link to that dead URL, while the real policy is the in-app route. The `analytics-consent` capability already requires that "the privacy policy SHALL name PostHog (Klant Solutions B.V., Netherlands) as the third-party recipient and enumerate the purpose of the cross-border transfer" — this change makes that page actually satisfy it and removes the broken links.

## Goals / Non-Goals

Goals:
- The in-app Privacy Policy content names PostHog (Klant Solutions B.V., Netherlands) as a named third-party cross-border recipient under APPI Article 28.
- The policy enumerates the categories of data transferred to PostHog and the purpose of that transfer.
- The two in-app links that currently point at `https://liverty.me/privacy` resolve to the in-app `/legal/privacy` route.
- The `legal-documents` spec records both obligations so future integrations keep the disclosure honest.

Non-Goals:
- No new analytics behaviour, no consent-gating change (the opt-out model under EU adequacy is unchanged; see `analytics-consent`).
- No new legal route, component, or i18n mechanism — content rides the existing `legal.privacy.sections[]` shape.
- No backend / proto / schema change.
- Not a substitute for legal counsel sign-off on the minor-user question (deferred elsewhere); this change discharges only the Article 28 disclosure.

## Decisions

- **Edit i18n content, not the component.** The `legal-document` component already renders an arbitrary `sections[]` array, so the disclosure is added by editing the en/ja `legal.privacy.sections` entries (the existing sections 4 "Provision to Third Parties", 5 "External Transmission", and 6 "Cross-Border Transfer" are the natural homes). No `.ts`/`.html`/`.css` change to the component is needed. Bump `legal.privacy.lastUpdated`.
- **Name the recipient explicitly.** The cross-border section states the recipient legal entity and country: PostHog Cloud EU, operated by Klant Solutions B.V., Netherlands. We disclose the named entity + country + categories + purpose as a matter of transparency; whether a generic "PostHog (EU)" mention would have legally sufficed under APPI Article 28 is a counsel judgement, not an engineering one (see Open Questions).
- **Enumerate categories + purpose.** The policy lists the data categories transferred to PostHog (interaction/usage events captured via cookies and localStorage — the non-PII catalogue) and the purpose (product analytics: improving the Service / measuring effectiveness). This satisfies 11.2.
- **In-app links, not external — reconcile, don't duplicate.** `settings-route.html` already has a working Privacy Policy link in the ABOUT section (~line 230) that calls `openLegal('/legal/privacy')` via the root router. The broken `href="https://liverty.me/privacy"` is a *separate* anchor (~line 201) attached to the analytics opt-out toggles. The fix is therefore to *reconcile / dedupe* the two: route the broken analytics-section anchor through the same existing `openLegal('/legal/privacy')` mechanism rather than adding a second link, and drop its `target="_blank"`/`rel="noopener noreferrer"` external treatment. `consent-route.html` has its own dead `https://liverty.me/privacy` anchor (~line 35) which is likewise re-pointed at in-app `/legal/privacy` navigation. Because the targets are in-app routes, the external-link treatment is no longer appropriate; use the app's normal in-app navigation.
- **Keep ja as the authoritative legal locale.** Author the ja copy as the source of truth and mirror it in en, consistent with the "Japanese is the primary locale for the legal content" requirement.

## Open Questions

- **Processor vs. third-party recipient — unestablished, blocks final copy.** Whether PostHog (Klant Solutions B.V.) acts as a *processor handling personal data on Liverty's behalf* or as an independent *third-party recipient* is not yet established. This classification materially changes the required disclosure wording (a processor relationship and a third-party provision are disclosed differently under APPI). This change drafts the disclosure naming the entity, country, categories, and purpose — facts that hold under either reading — but does NOT assert the classification as settled. The policy owner / legal counsel MUST confirm the classification before the copy is finalized and released. Engineering does not decide this.
- **APPI Article 28 sufficiency.** Whether the chosen wording legally satisfies APPI Article 28 (and which sub-clauses apply given the classification above) is for counsel to confirm; the spec deliberately does not encode a sufficiency judgement.

## Risks / Trade-offs

- **Legal accuracy.** The disclosure wording is a compliance artifact, and the processor-vs-recipient classification (see Open Questions) is unresolved. Mitigation: a task requires the policy owner / counsel to confirm the classification and review the copy before release; engineering provides the structurally-correct draft (recipient named, country + categories + purpose enumerated) but does not finalize legal wording or assert the legal classification unilaterally.
- **ja/en drift.** Editing two locale files risks the disclosures diverging. Mitigation: change both in the same edit and keep the section structure parallel; `make lint`/build covers JSON validity.
- **Link-treatment regression.** Switching from an external `<a target="_blank">` to in-app navigation changes the markup; Aurelia routing must resolve `/legal/privacy`. Mitigation: the route already exists and is a registered public route (per `legal-documents` spec); verify via build + a manual click.
- **Spec already references PostHog Cloud EU.** `analytics-consent` and the existing `legal-documents` Privacy Policy requirement already mention the EU transfer; this change tightens "PostHog Cloud EU" to the named legal entity, so the two specs stay consistent rather than contradicting.
