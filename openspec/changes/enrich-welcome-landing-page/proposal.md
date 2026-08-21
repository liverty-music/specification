## Why

The Welcome page (`/`) is the product's only landing page (LP), but today it demonstrates just one of the three core value pillars — the auto-collected concert timetable — and leaves the other two (ticket/goods info, new-concert push notifications) invisible. Its two-screen hard-snap layout and single hero fade-in read as a "static page" rather than a refined product, so a first-time visitor rarely feels what Liverty Music actually does before deciding to leave. This change turns the Welcome page into a value-communicating LP that shows all three real capabilities through the product's own UI, with scroll-driven storytelling — following LP best practice and the motion/whitespace craft of references like feather.art.

## What Changes

- Convert the Welcome page from a two-screen hard-snap layout into a **continuous scrolling narrative** (hero stays full-viewport; subsequent sections flow) with **scroll-reveal** on section entry (`IntersectionObserver`, fade + slide-up), fully disabled under `prefers-reduced-motion`.
- **Keep the hero screen unchanged**: brand glow, `title` / `subtitlePain` / `subtitleAction` copy, the emphasized-verb glow, the language switcher, and the existing scroll-affordance CTA (`サンプルを覗く` / `Peek at a sample`) all remain as-is.
- Add a **timetable section** that reuses the existing read-only `concert-highway` preview (the concert auto-collection pillar) as a complete, composed frame — no cropped "half-peek".
- Add a **ticket/goods section** that embeds the existing event detail view (from `event-detail-sheet`) in a read-only, non-sheet form, showing official-info (`sourceUrl`), merch (`merchUrl`), venue, and calendar affordances. The authenticated-only ticket-journey block naturally stays hidden for the anonymous visitor. It plays a **Lv2 arrival motion** (the detail card rises once on entry).
- Add a **new-concert notification section** with a **new notification mock card** (real OS push cannot be shown inside a page), playing a **Lv2 arrival motion** (drop-in + a single bell nudge).
- Preserve the existing **two-layer CTA structure**: the hero exposes only the soft scroll affordance; the commit CTAs (`Get Started` / `Log In`) remain after the value is communicated, at the final CTA section. The no-preview-data fallback (inline CTAs on the hero) is preserved.
- Restrict shown capabilities to the **three that actually exist** (concert-info auto-collection, ticket/goods info, new-concert push). Do **not** introduce phone-frame device chrome, trust numbers/stats, or social proof (the service is pre-launch with no such material).

## Capabilities

### New Capabilities
<!-- None. This change enriches an existing capability's presentation and behavior. -->

### Modified Capabilities
- `landing-page`: Add requirements for scroll-reveal storytelling behavior, the timetable value section, the ticket/goods value section (read-only embed of the event detail view), and the new-concert notification mock section with its arrival motion. The existing hero, two-layer CTA, scroll-affordance, guest-friendly copy, language switcher, and authenticated-redirect requirements are unchanged except where the added sections extend the scroll target and reveal behavior.

## Impact

- **Frontend only.** No proto/backend/RPC changes; no BSR gen. Uses the existing `ConcertStore.listByArtists` preview path and curated `previewArtistIds` from runtime `config.json`.
- Affected code: `src/routes/welcome/` (`welcome-route.html` / `.css` / `.ts` / `.stories.ts`), locale files `src/locales/{ja,en}/translation.json` (new section copy; hero keys untouched).
- Reused components: `concert-highway` (read-only), `event-detail-sheet` (its `sheet-content` extracted/embedded as a read-only view), `svg-icon`.
- New component: a notification mock card for the notification section.
- Motion utility: a shared scroll-reveal mechanism (`IntersectionObserver`) honoring `prefers-reduced-motion`; INP/perf kept in check by preferring Lv2 one-shot arrival motions over continuous loops.
- Residual risk to resolve in design: the preview depends on live concert data for curated artists and can be empty — the page must degrade gracefully (existing fallback) and the added sections must not break when preview data is unavailable.
