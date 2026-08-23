## 1. Reset the prior iteration

- [x] 1.1 Remove the `EventDetailContent` component (`event-detail-content.ts/.html/.css`) and its `main.ts` registration (superseded by opening the real `event-detail-sheet`) (D3)
- [x] 1.2 Remove the standalone §3 detail section and §4 notification section markup/CSS from the prior stacked-sections layout; keep the notification mock card component (reused as demo step S0)
- [x] 1.3 Restore the timetable to its full composed height (undo the `60svh` compression) (D7)

## 2. Hero kinetic brand + ambient background (always-on life)

- [x] 2.1 Add a gradient-clipped spotlight shimmer to the `LIVERTY MUSIC` wordmark using the existing festival-spotlight palette; compositor-only (`background-position`), disabled under `prefers-reduced-motion` (falls back to the current static glow) (D6)
- [x] 2.2 Add a fixed, full-page, `pointer-events: none`, `mix-blend-mode: screen` canvas rendering a sparse drifting particle glow behind all content (brand-accent palette); cap particle count/DPR, pause when hidden/offscreen, disable under reduced motion (D6)
- [x] 2.3 Verify the ambient background never intercepts pointer input and keeps foreground content legible

## 3. Interactive timetable + detail sheet

- [x] 3.1 Drop `is-readonly` on the Welcome `concert-highway` and wire its `event-selected` → the real `event-detail-sheet.open(event)` (D3)
- [x] 3.2 Render `event-detail-sheet` on the Welcome route; confirm the `isAuthenticated`-gated ticket-journey stays hidden for the anonymous visitor and merch/official/venue/calendar surface
- [x] 3.3 Resolve the sheet's `history.pushState('/concerts/:id')` on the Welcome route — verify the route tolerates the pushed URL + `popstate` close, or suppress `pushState` in the LP context (D3, Risks)
- [x] 3.4 Present the timetable as a complete composed frame (no cropped peek); communicate "auto-collected from your followed artists"

## 4. Guided demo sequence (state machine)

- [x] 4.1 Build the demo state machine S0→S3 with a one-shot IntersectionObserver trigger on scroll-into-view (D2)
- [x] 4.2 S0: mock new-concert notification (real-OS-push-style card with the PWA icon) drops in with an attention-drawing entrance (overshoot); a pulsing hint invites the tap (D2)
- [x] 4.3 S0→S1 advance: tap advances immediately; auto-advance after a short interval if untouched (auto-advance-with-interrupt) (D2)
- [x] 4.4 S1 transition: sequential dismiss → appear — a `demoExiting` flag plays the notification's exit, and only after it fully leaves (`NOTIF_EXIT_MS`, aligned to the CSS exit duration) does the view-model swap to the timetable; the two never overlap. (Supersedes the originally-planned View Transitions morph — the cross-fade overlapped exit + entrance; a clean hand-off reads better and needs no feature-detect/fallback.) (D5)
- [x] 4.5 S2: once the timetable is interactive, show a `coach-mark` on the first concert card ("tap to see tickets, goods, venue"); light-dismiss preserved; no hover dependency (D4)
- [x] 4.6 Mobile-first affordance: convey card tappability via the coach-mark + a touch `:active` press state (no hover glow) (D4)

## 5. Reduced-motion / no-JS / fallback

- [x] 5.1 Under `prefers-reduced-motion` (or script failure): skip the notification, its entrance cue, and the transition — present the interactive timetable directly with a static "tap a card" hint; keep it fully usable (spec: reduced-motion + content-present-without-motion)
- [x] 5.2 Preserve the no-preview fallback: when preview data is unavailable, render neither the demo nor the timetable; the hero shows inline `[Get Started]` / `[Log In]` CTAs and no scroll-affordance

## 6. Copy + scope

- [x] 6.1 Add/adjust demo copy (notification text, coach-mark guidance, section framing) in `translation.json` (JA/EN); do not touch `welcome.hero.*`
- [x] 6.2 Confirm no capability beyond the three real pillars is advertised, and no phone-frame chrome / stats / social proof / name marquee is introduced (D1, scope requirement)
- [x] 6.3 Fix the dev-only `?devPreview=1` mock data to distribute concerts across HOME / NEAR / AWAY lanes like real data (never ships) (D8)

## 7. Tests

- [x] 7.1 Update/extend `welcome-route.stories.ts` for the data-present (demo) and data-absent (fallback) states
- [x] 7.2 Add/adjust unit tests: demo state transitions (S0→S1 tap and auto-advance), sequential dismiss → appear timing (`demoExiting` held for `NOTIF_EXIT_MS` before the timetable swaps in), reduced-motion skip path, card-tap → sheet-open wiring, no-preview fallback
- [x] 7.3 Run `make check` (lint + typecheck + unit tests) and fix issues

## 8. Post-implementation localhost verification (manual, required)

- [x] 8.1 `npm start` and open the Welcome page (`/`) on localhost as an unauthenticated visitor (`?devPreview=1` for demo data without a backend)
- [x] 8.2 Verify the full demo: notification drops in → tap (and separately, auto-advance) → notification dismisses → interactive timetable → coach-mark → card tap opens the real detail sheet
- [x] 8.3 Verify the hero kinetic shimmer and the ambient background read as alive but calm, and content stays legible
- [x] 8.4 Confirm real curated data distributes across lanes; then exercise the no-preview state and confirm graceful degradation to the hero inline-CTA fallback
- [x] 8.5 Enable `prefers-reduced-motion` and confirm the demo is skipped, the interactive timetable is shown directly, and all ambient/kinetic motion stops while content stays readable
- [x] 8.6 Check mobile width (real device or DevTools): tappability is clear without hover, canvas stays smooth, layout holds (no phone-frame; native/full-bleed)

## 9. Ship

- [x] 9.1 Open the frontend PR (Conventional Commits, mandatory body + `Refs: #<issue>`), pass CI (PR #561)
- [x] 9.2 Merge and cut the frontend release to prod; confirm the prod pin-bump reaches ArgoCD and the change is live (v1.58.0; fan-web prod pin + ArgoCD rollout verified live)

## 10. Follow-up: bound the demo screen so the CTA stays visible (D7)

- [x] 10.1 Give `.welcome-demo` a *definite* block-size (`block-size`/`max-block-size: 100svh`, not just `min-block-size`) so the `flex: 1` → grid `1fr` → `concert-highway { block-size: 100% }` chain resolves; the timetable then fills the demo screen with `concert-highway`'s internal scroll and the CTA footer stays pinned on-screen (D7)
- [x] 10.2 Add `overflow: hidden` to `.welcome-preview` so the internally-scrolled timetable is clipped at the bottom fade mask and never spills past the demo screen (D7)
- [x] 10.3 Localhost verify (`?devPreview=1`, incl. 390px mobile): the demo section is exactly one snap screen, the CTA footer (`Get Started` / `Log In`) is visible without scrolling past the demo, and `concert-highway` scrolls internally to reveal later dates; re-check the coach-mark still anchors the first card and reduced-motion still shows the timetable directly

  Measured (412px width): demo `clientHeight == innerHeight` (915→915, was ~3797px); CTA footer bottom 866 ≤ 915 (visible); `document` no longer overflows (scrollHeight == 915). At a short 560px viewport (forces overflow): `.concert-scroll` becomes scrollable (clientH 192 / scrollH 502) and `scrollTop` moves 0→310 — later dates stay reachable, not clipped; CTA still visible (bottom 511 ≤ 560); `[data-live-card]` present for the coach-mark. Preview `overflow: hidden` confirmed; reduced-motion block untouched.
