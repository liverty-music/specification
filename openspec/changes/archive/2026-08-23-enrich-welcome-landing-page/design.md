## Context

See proposal.md — Why. Current state (verified against `frontend/src/routes/welcome/` and the live component behavior):

- The Welcome page is a two-screen `scroll-snap-type: y proximity` layout: Screen 1 (hero, `100svh`) and Screen 2 (`100svh`) holding the read-only `concert-highway` preview plus the CTA footer. The original Screen 2 timetable is well-composed: with real preview data, concerts distribute across the HOME / NEAR / AWAY lanes and read as a full, living timetable.
- The hero already implements the "message-first" two-layer CTA: with preview data, Screen 1 shows only the scroll-affordance (`welcome.hero.seePreview` = `サンプルを覗く`) and the language switcher; the commit CTAs live only in Screen 2's footer. Without preview data (`dateGroups.length === 0`) the commit CTAs fall back inline to the hero.
- Preview data comes from `ConcertStore.listByArtists(previewArtistIds, 'JP', 'JP-13', …)` where `previewArtistIds`/`previewArtistNames` are curated in runtime `config.json`. Preview renders only when at least `PREVIEW_MIN_ARTISTS_WITH_CONCERTS` (5) curated artists resolve concerts; otherwise it silently degrades to the no-preview fallback. Preview concerts use synthetic `hype: 'watch'` for the softer "unmatched" faded-poster treatment.
- `concert-highway` cards fire a bubbling `event-selected` CustomEvent on tap **unless** `readonly` is set (see `event-card.ts`: `onClick()` returns early when `readonly`). The dashboard wires `event-selected.trigger` → `EventDetailSheet.open(event)`. The Welcome page currently sets `is-readonly="true"`, which is why the cards do not open.
- `event-detail-sheet` renders concert detail inside a `bottom-sheet` and already surfaces official-info (`sourceUrl`), merch (`merchUrl`, gated by `hasMerchUrl`), venue + Google Maps, and calendar. Its ticket-journey block is gated by `isAuthenticated`, so it is naturally hidden for the anonymous visitor. It `history.pushState`s `/concerts/:id` on open and closes on `popstate`.
- `coach-mark` is a built component (`targetSelector`, `message`, `active`, `onTap`, `onDismiss`) that spotlights a target element via CSS anchor positioning and light-dismisses on outside tap. It is currently driven app-shell-wide by `CoachMarkService` for onboarding.
- Styling follows CUBE CSS (`@layer` / `@scope`) with design tokens (`--step-*`, `--space-*`) and a "festival-spotlight glow" brand vocabulary (brand-accent `text-shadow`) already used by the hero and event cards. The stack already uses canvas (dna-orb).

Reference analysis (Designship 2026, measured): its "alive" quality comes from **ambient, always-on motion**, not entrance reveals — kinetic gradient-clipped display type (`background-position` shimmer), a fixed full-page `mix-blend-mode: screen` particle canvas, radar-ping dots, and pervasive micro-interactions — over a dark surface (`rgb(27,29,39)`) nearly identical to Liverty's. The prior iteration of this change under-delivered because it relied on subtle entrance reveals over a flat, centered layout with no ambient motion.

## Goals / Non-Goals

**Goals:**
- Communicate all three pillars through one **guided product demo** that replays the real user journey (push → open → timetable → detail), reusing the product's own components.
- Make the page feel alive with **ambient, always-on motion** (kinetic brand, ambient background) rather than relying on entrance reveals alone.
- Keep the hero's message, two-layer CTA, language switcher, scroll-affordance, and no-preview fallback intact.
- Mobile-first: no interaction depends on hover.

**Non-Goals:**
- No changes to the preview data source, the curated-artist mechanism, or the `PREVIEW_MIN_ARTISTS_WITH_CONCERTS` threshold.
- No phone-frame device chrome, no stats/trust numbers, no social proof, no name marquee.
- No new capabilities advertised beyond the three existing pillars.
- No backend/proto/RPC/BSR work — frontend only.

## Decisions

### D1. One guided demo replaces stacked value sections

Below the hero, a single demo section unifies all three pillars into one connected flow instead of three separate stacked sections. The narrative *is* the product's real journey. Rationale: telling three features as one felt experience beats three explained cards; it lowers cognitive load and demonstrates the actual loop. Alternative — three independent sections — rejected as the prior iteration; it read as a static, disconnected page.

### D2. Demo state machine (scroll-triggered, auto-advance-with-interrupt)

```
S0 Notification  → mock OS-push card drops in (overshoot) + pulsing tap hint
   │  tap  ───────────────► advance immediately (demonstrates "tap a push")
   │  no interaction ~4s ─► auto-advance (demo always completes)
S1 Transition    → notification dismiss → (fully leaves) → timetable appears
S2 Timetable     → interactive; coach-mark points at first card
   │  tap card ─────────► open real event-detail-sheet
S3 Detail sheet  → official-info / merch / venue+map / calendar
                    (ticket-journey hidden: isAuthenticated === false)
```

The sequence starts when the demo scrolls into view (one-shot IntersectionObserver). Rationale: auto-advance-with-interrupt gives active users agency (the tap is itself the demo) while guaranteeing passive users see the whole story. No "hero-adjacent auto-play" — the visitor must scroll to it for the trigger to make sense. No replay control (keeps the surface clean; the end state is a usable timetable).

### D3. Interactive timetable opens the real sheet — delete the static embed

Drop `is-readonly` on the Welcome `concert-highway`; wire its `event-selected` → the real `event-detail-sheet.open(event)`. The ticket/goods pillar is demonstrated by *touching the real product*. The `EventDetailContent` component added in the prior iteration is **removed**. Rationale: the real sheet IS the feature; a bolted-on static card is redundant and lower-fidelity. The `isAuthenticated` gate already hides ticket-journey for guests. Open question resolved in Risks: the sheet's `history.pushState('/concerts/:id')` on the Welcome route.

### D4. Coach-mark provides the tap affordance (mobile-first, no hover)

A `coach-mark` spotlights the first concert card with "tap to see tickets, goods, and venue" once the timetable becomes interactive (S2). Rationale: hover is a pointer/desktop-only signal; on touch it does not exist. The coach-mark makes tappability explicit for everyone and converts passive viewers into explorers. Touch feedback on activation is a `:active` press state, not a hover glow. Alternative — hover glow to imply interactivity — rejected (fails on mobile, the primary target).

### D5. Notification → timetable via a sequential dismiss → appear transition

The S1 transition is **sequential**: tapping (or auto-advance) sets a `demoExiting` flag that plays the notification's dismiss animation, and only once it has fully left (`NOTIF_EXIT_MS`, aligned to the CSS exit duration) does the view-model swap `demoPhase` to `timetable`, which plays its own entrance. The two views never overlap.

This replaces the originally-planned View Transitions morph (`document.startViewTransition` with a shared `view-transition-name`). The cross-fade morph made the notification exit and the timetable entrance play *simultaneously*, which read as a muddled overlap rather than "one thing became the next"; a clean dismiss-then-appear communicates the hand-off more legibly and needs no feature-detection or fallback branch. Rationale unchanged: continuity and demonstrating the product loop through motion. Under reduced motion the demo is skipped and the interactive timetable is presented directly.

### D6. Kinetic brand + ambient background = always-on life

- **Kinetic brand:** the "LIVERTY MUSIC" wordmark gets a gradient-clipped spotlight shimmer (animated `background-position`), extending the existing festival-spotlight vocabulary. Compositor-only; disabled under reduced motion (falls back to the current static glow).
- **Ambient background:** a fixed, full-page, `pointer-events: none`, `mix-blend-mode: screen` canvas renders a sparse drifting particle glow (Designship-faithful technique; Liverty brand-accent palette, not Designship's colors). It sits behind all content, adds depth, and reinforces the "signals in the air" discovery theme. Disabled/frozen under reduced motion.

Rationale: the reference's aliveness is ambient, not entrance-based. These two always-on effects carry the "living product" feel; entrance reveals become garnish, not the main event.

### D7. Hero message and two-layer CTA preserved; timetable fills the demo screen (bounded, internal-scroll)

Hero copy, language switcher, scroll-affordance label (`seePreview`), and the no-preview inline-CTA fallback are unchanged. The commit CTAs (`Get Started` / `Log In`) remain after the demo in a final CTA section (two-layer intent from `Passkey Authentication CTA`).

The timetable is presented at its full, composed height — meaning it **fills the demo screen**, undoing the prior iteration's `60svh` compression that made it feel cramped. "Full height" here means the timetable fills the demo section's `1fr` row and reveals additional dates through `concert-highway`'s own internal scroll (`.concert-scroll`, with a bottom fade-out mask) — it does **not** mean the demo section expands unbounded to fit every date group.

The demo section is one snap screen: it is bounded to the small-viewport height (`100svh`), a definite height so the `flex: 1` → grid `auto 1fr auto` → `1fr` preview → `concert-highway { block-size: 100% }` chain resolves and the CTA footer stays pinned on-screen. Gotcha (the defect this reconciles): bounding the section with `min-block-size` alone leaves it content-sized, so every downstream `1fr` / `flex: 1` / `100%` collapses to natural height, `concert-highway`'s internal scroll never engages, the timetable expands to ~3800px, and the CTA footer is pushed off-screen. The section needs a *definite* height (`block-size`/`max-block-size: 100svh`), not just a minimum; the downstream `min-block-size: 0` on the grid and preview are already in place to let those rows shrink. Guard the timetable's overflow (`overflow: hidden` on the preview) so nothing spills past the fade mask.

### D8. Fix preview mock data distribution (dev only)

The dev-only `?devPreview=1` mock data must distribute concerts across HOME / NEAR / AWAY lanes like real data, not dump everything in one lane (which made the grid look broken during review). This is a local review aid, gated by `import.meta.env.DEV`; it never ships.

## Risks / Trade-offs

- **Preview data can be empty** (fewer than 5 curated artists resolve concerts) → the whole demo is preview-dependent. Mitigation: preserve the existing no-preview fallback (inline hero CTAs, no scroll-affordance); the demo renders only when preview data exists, so it disappears cleanly in the fallback. The localhost check must exercise both paths.
- **Transition timing / reduced motion** → the sequential dismiss → appear relies on `NOTIF_EXIT_MS` matching the CSS exit duration; if they drift, the timetable could appear before the notification finishes leaving. Mitigation: keep the JS constant and the CSS keyframe duration aligned (D5). Under reduced motion the demo is skipped and the interactive timetable is shown directly. Both paths end at the same interactive timetable.
- **Auto-advance and assistive technology** → an auto-dismissing/auto-advancing sequence can disorient screen-reader and motor-impaired users. Mitigation: the timetable end state is always reachable and interactive; under reduced motion the demo is skipped and the interactive timetable is shown directly (spec: reduced-motion + "content present without motion"). The notification is decorative; nothing essential is gated behind the animation.
- **Detail sheet `pushState` on the Welcome route** → opening the real sheet pushes `/concerts/:id`. Mitigation: verify the Welcome route tolerates the pushed URL and `popstate` close, or suppress `pushState` in the LP context; confirm no router teardown of the Welcome component.
- **Canvas performance on mobile** → a full-page particle canvas can cost battery/INP. Mitigation: sparse particles, `transform`/`opacity`-style compositing via `mix-blend-mode`, cap particle count and DPR, pause when offscreen/hidden, and disable under reduced motion. Verify on a real mobile width.
- **Extra always-on motion vs calm** → ambient shimmer + particles must stay subtle, not distracting. Mitigation: low contrast/opacity, slow periods; all disabled under reduced motion.

## Open Questions

- Whether the S0→S1 auto-advance interval and the dismiss/entrance durations need tuning after the localhost check — a copy/timing detail that does not change the specs or task breakdown.
- Whether to later extend the ambient background from canvas to a WebGL variant — deferred; the CSS/2D-canvas version ships first.
