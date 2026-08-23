## Why

The Welcome page (`/`) is the product's only landing page (LP), but today it demonstrates just one of the three core value pillars — the auto-collected concert timetable — and leaves the other two (ticket/goods info, new-concert push notifications) invisible. Its two-screen hard-snap layout and single hero fade-in read as a "static page" rather than a refined product, so a first-time visitor rarely feels what Liverty Music actually does before deciding to leave. This change turns the Welcome page into a value-communicating LP that shows all three real capabilities through the product's own UI, with a **guided product demo** that replays the actual user journey — following LP best practice and the motion/atmosphere craft of references like Designship 2026.

## What Changes

- **Keep the hero screen's message and two-layer CTA**: brand, `title` / `subtitlePain` / `subtitleAction` copy, the emphasized-verb glow, the language switcher, and the existing scroll-affordance CTA (`サンプルを覗く` / `Peek at a sample`) all remain. The brand wordmark gains a **kinetic spotlight shimmer** (an animated gradient sweep, using the existing festival-spotlight palette) so the hero reads as a living, always-on product rather than static text.
- Add an **ambient background** across the page — a faint, screen-blended particle glow rendered on a fixed full-page canvas, evoking "signals in the air" (concerts out there waiting to be surfaced) and giving the flat dark surface depth. Disabled under `prefers-reduced-motion`.
- Replace the previous "three stacked value sections" idea with a single **guided product demo** that unifies all three pillars into one connected flow, triggered when the visitor scrolls it into view:
  1. **S0 — Notification**: a mock new-concert push notification (a real-OS-push-style card with the PWA icon) drops in with an attention-drawing entrance; a pulsing hint invites the tap — the push-notification pillar.
  2. **S1 — Tap / auto-advance**: the visitor taps the notification (demonstrating "tap a push"); if untouched after a short beat it auto-advances, so the demo always completes.
  3. **S1→S2 — Transition**: the notification is **dismissed, and once it has fully left the concert timetable appears** (a sequential hand-off, not an overlapping cross-fade), filling the demo screen — the auto-collection pillar.
  4. **S2 — Interactive timetable + coach-mark**: the timetable is now interactive; a coach-mark points at a concert card ("tap to see tickets, goods, and venue").
  5. **S3 — Detail sheet**: tapping a card opens the product's real `event-detail-sheet` showing official-info (`sourceUrl`), merch (`merchUrl`), venue + map, and calendar — the ticket/goods pillar. The `isAuthenticated`-gated ticket-journey naturally stays hidden for the anonymous visitor.
- Make the Welcome timetable **interactive** (remove the `is-readonly` preview gate; wire `event-selected` → the real sheet) so the ticket/goods pillar is demonstrated by *touching the real product*, not by a bolted-on static card. The previously-added `EventDetailContent` component is **removed**.
- Preserve the existing **two-layer CTA structure**: the hero exposes only the soft scroll affordance; the commit CTAs (`Get Started` / `Log In`) remain after the demo, in a final CTA section. The no-preview-data fallback (inline CTAs on the hero) is preserved.
- **Mobile-first**: interaction affordances do not depend on hover (a pointer/desktop-only signal). Card tappability is conveyed by the coach-mark and a touch `:active` press state.
- Restrict shown capabilities to the **three that actually exist** (concert-info auto-collection, ticket/goods info, new-concert push). Do **not** introduce phone-frame device chrome, trust numbers/stats, social proof, or a name marquee (the service is pre-launch with no such material, and a generic artist marquee would dilute the personalization message).

## Capabilities

### New Capabilities
<!-- None. This change enriches an existing capability's presentation and behavior. -->

### Modified Capabilities
- `landing-page`: Add requirements for the guided product-demo sequence (notification → dismiss → interactive timetable → detail sheet), the interactive-timetable detail behavior (real sheet on card tap, ticket-journey hidden for guests), the hero kinetic brand treatment, and the ambient background. The existing hero message, two-layer CTA, scroll-affordance, guest-friendly copy, language switcher, and authenticated-redirect requirements are unchanged except where the demo extends the scroll target and entry behavior. Motion is disabled under reduced motion, and content remains present and reachable without it.

## Impact

- **Frontend only.** No proto/backend/RPC changes; no BSR gen. Uses the existing `ConcertStore.listByArtists` preview path and curated `previewArtistIds` from runtime `config.json`.
- Affected code: `src/routes/welcome/` (`welcome-route.html` / `.css` / `.ts` / `.stories.ts`), locale files `src/locales/{ja,en}/translation.json` (demo copy; hero keys untouched).
- Reused components: `concert-highway` (now **interactive** on the LP), `event-detail-sheet` (opened by card tap — no new embed component), `coach-mark` (guides the tap), `svg-icon`.
- New component: a notification mock card for the demo's S0 step.
- Removed: the `EventDetailContent` component (superseded by opening the real sheet).
- Motion utility: a scroll-into-view trigger for the demo; a sequential dismiss → appear transition for the notification→timetable hand-off (CSS keyframes gated by a `demoExiting` flag; no View Transitions dependency); a fixed full-page canvas for the ambient glow. All honor `prefers-reduced-motion` and keep INP in check (transform/opacity, one-shot, no continuous per-frame layout work).
- Residual risks to resolve in design: the preview depends on live concert data for curated artists and can be empty — the page must degrade gracefully (existing fallback) and the demo must not break when preview data is unavailable; the transition and canvas need reduced-motion paths; auto-advance must not trap assistive-technology users.
