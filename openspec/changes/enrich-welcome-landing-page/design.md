## Context

See proposal.md — Why. Current state (verified against `frontend/src/routes/welcome/`):

- The Welcome page is a two-screen `scroll-snap-type: y proximity` layout: Screen 1 (hero, `100svh`) and Screen 2 (`100svh`) holding the read-only `concert-highway` preview plus the CTA footer.
- The hero already implements the "message-first" two-layer CTA: with preview data, Screen 1 shows only the scroll-affordance (`welcome.hero.seePreview` = `サンプルを覗く`) and the language switcher; the commit CTAs (`Get Started` / `Log In`) live only in Screen 2's footer. Without preview data (`dateGroups.length === 0`) the commit CTAs fall back inline to the hero.
- Preview data comes from `ConcertStore.listByArtists(previewArtistIds, 'JP', 'JP-13', …)` where `previewArtistIds`/`previewArtistNames` are curated in runtime `config.json`. Preview renders only when at least `PREVIEW_MIN_ARTISTS_WITH_CONCERTS` (5) curated artists resolve concerts; otherwise it silently degrades to the no-preview fallback. Preview concerts use synthetic `hype: 'watch'` on purpose to get the softer "unmatched" faded-poster treatment.
- The only motion today is `animation: fade-in 600ms ease-out both` on the hero, already disabled under `prefers-reduced-motion`.
- `event-detail-sheet` renders concert detail inside a `bottom-sheet` and already surfaces official-info (`sourceUrl`), merch (`merchUrl`, gated by `hasMerchUrl`), venue + Google Maps, and calendar. Its ticket-journey block is gated by `isAuthenticated`, so it is naturally hidden for the anonymous visitor.
- Styling follows CUBE CSS (`@layer` / `@scope`) with design tokens (`--step-*`, `--space-*`) and a "festival-spotlight glow" brand vocabulary (brand-accent `text-shadow`) already used by the hero and event cards.

## Goals / Non-Goals

**Goals:**
- Show all three real value pillars through the product's own UI, in a continuous scroll narrative with entrance-only reveal motion.
- Keep the hero byte-for-byte behaviorally identical (copy, glow, language switcher, scroll-affordance label, two-layer CTA, fallback).
- Reuse existing components (`concert-highway`, the `event-detail-sheet` content) rather than adding illustrations or device chrome.
- Keep motion cheap and calm: entrance-only reveals + one-shot (Lv2) arrival motions, never continuous loops.

**Non-Goals:**
- No changes to the preview data source, the curated-artist mechanism, or the `PREVIEW_MIN_ARTISTS_WITH_CONCERTS` threshold.
- No phone-frame device chrome, no stats/trust numbers, no social proof.
- No new capabilities advertised beyond the three existing pillars.
- No backend/proto/RPC/BSR work — frontend only.

## Decisions

### D1. Continuous scroll narrative, hero keeps its snap

Replace the rigid two-`100svh`-snap model with: hero stays `100svh` and keeps `scroll-snap-align: start`; the value sections below flow in a continuous column with a consistent vertical rhythm (feather-like breathing room via `--space-*`). Rationale: three pillars cannot be told in two hard-snapped screens; a narrative needs room. Alternative considered — keep snapping every section — rejected: hard snap fights storytelling and makes reveal timing feel abrupt.

### D2. Scroll-reveal via a shared `IntersectionObserver` utility

A single reveal mechanism observes each value section and toggles a "revealed" state on first entry; CSS drives the entrance-only fade + short upward slide. It honors `prefers-reduced-motion` by rendering the final state immediately (no observer-driven animation, or the CSS transition is nulled). Rationale: one source of truth for reveal, no per-section bespoke JS, cheap for INP. Alternative — CSS `animation-timeline: view()` (scroll-driven CSS) — attractive but browser support/consistency is still uneven for a launch LP; keep it as a possible later simplification. **Content must be in the DOM and reachable even if the observer never fires** (spec: "Content is present without motion").

### D3. Reuse the event-detail-sheet content as a read-only embed (§3)

Extract the sheet's inner content (`sheet-content`: hero image, artist header, detail rows, official/merch/calendar footer) so it can render outside `bottom-sheet` in a static, read-only card on the LP. The ticket-journey `isAuthenticated` gate keeps auth-only controls hidden for the anonymous visitor with no extra logic. Rationale: the real detail UI *is* the feature demo; extracting the content view also makes it reusable beyond the LP. Alternative — render the whole `bottom-sheet` "open and pinned" — rejected: couples the LP to sheet/backdrop/dismiss behavior and fights the page's scroll.

### D4. Motion levels — Lv2 one-shot arrival for §3 and §4

- §3 (ticket/goods): the detail card **rises once** into place on section entry.
- §4 (notification): a **new mock notification card** **drops in** with a single brief bell nudge on entry.

Both are one-shot on first reveal, layered on top of the D2 reveal, and disabled under reduced motion. Rationale: arrival motion reads as refined and "alive" without the INP/perf cost and visual noise of continuous (Lv3) loops. Alternative — Lv3 looping demos (feather-style tap→open loop, rotating notifications) — deferred; can be revisited after seeing Lv2 in the localhost check.

### D5. Notification section content is a mock card, not a live push (§4)

Real OS push cannot render inside a page, so §4 uses a purpose-built mock card styled to read as a Liverty new-concert alert (bell, brand, sample artist line). Rationale: honestly represents the value without faking system UI. Copy is added to `translation.json` (JA/EN); no new capability is implied.

### D6. Commit-CTA placement preserved via a final CTA section

The commit CTAs remain after the value content in a final CTA section (the role Screen 2's footer plays today), preserving the two-layer intent from `Passkey Authentication CTA` (CTAs never on the hero when preview exists). The no-preview fallback (inline hero CTAs) is untouched.

### D7. Hero is untouched

No edits to hero markup/copy/CSS beyond what D1 requires structurally (the scroll target is now the first value section rather than a single Screen 2). `welcome.hero.*` keys, including `seePreview` (`サンプルを覗く`), are unchanged.

## Risks / Trade-offs

- **Preview data can be empty** (fewer than 5 curated artists resolve concerts) → the whole value-section stack is preview-dependent. Mitigation: preserve the existing no-preview fallback (inline hero CTAs, no scroll-affordance); §3/§4 render only within the value-section stack, so they disappear together with §2 in the fallback — the page never shows a half-built narrative. The localhost check must exercise both the data-present and data-absent paths.
- **Reveal motion hiding content if JS/observer fails** → Mitigation: author CSS so the un-revealed state is still readable (e.g., start near-final, or apply the "hidden" pre-state only when a `js-enabled`/observer-ready flag is set), and always render content in the DOM. Verified by the "Content is present without motion" scenario.
- **INP/scroll jank on mobile** from observers + motion → Mitigation: one shared observer, `transform`/`opacity`-only animations, one-shot (not looping) arrivals, unobserve after first reveal.
- **Extracting `sheet-content` could regress the real sheet** → Mitigation: extract into a shared content view consumed by both the sheet and the LP; keep the sheet's existing tests green.
- **Longer page = more to keep responsive** → Mitigation: reuse existing tokens/spacing; verify mobile width in the localhost check (no phone frame means UI renders at native/full-bleed size).

## Open Questions

- Whether to later upgrade §3/§4 to Lv3 looping demos, or adopt scroll-driven CSS (`animation-timeline: view()`) once support is comfortable. Deferring these does not change the specs, the approach, or the task breakdown.
