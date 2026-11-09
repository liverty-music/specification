## Context

See proposal.md for the motivation. The decisions below were reviewed with the owner on an interactive plan page and with motion samples run in Chromium 156; this document records the result.

- The timetable (`<concert-highway>`) builds a window of 12 date groups (`WINDOW_SIZE`, `src/components/live-highway/concert-highway.ts:9`) and grows it by 12 when an edge marker comes within half a screen (`IntersectionObserver`, `rootMargin: '50% 0px'`, `:226`). Groups added above go through `keepingPlace()` (`:209`), which restores the date at the top of the screen with `scrollIntoView()` plus an offset (`:326-331`). The scroll container opts out of browser scroll anchoring (`overflow-anchor: none`, `concert-highway.css:91`).
- `meet-timetable-render-budget` measured about 280 ms to render one 12-date window on the reference profile, above the 200 ms bound. Anything this change adds to a render must stay out of that path.
- The event card has had no entrance since a staggered reveal on the date group was removed: "every row moved together despite correctly staggered delays" (`event-card.css:29-36`).
- View Transitions are called in two places, each behind `if (document.startViewTransition)`: `my-artists-route.ts:295` and `discovery-route.ts:405`, the latter also behind a `matchMedia('(prefers-reduced-motion: reduce)')` check. `global.css:89-110` styles the `root` transition and its `vt-suppress-root` variant.
- The fan app has one shell: `app-shell.html` renders a plain `<au-viewport>`. No route transition exists, although `app-shell` "Page Transition Animations" requires one for every route.
- The confirm dialog opens with `showModal()` and detects a backdrop tap in `onClick` (`confirm-dialog.ts:82-84`). The bottom sheet is a `<dialog popover="manual">` whose closing is driven by its own scroll; it is not touched.
- Fonts come from Google Fonts (`index.html:52`); the plain stack is `"Noto Sans JP", "Hiragino Sans", "Yu Gothic UI", system-ui, sans-serif` (`shared/styles/m3-sys.css:58`). Google's CSS has no `local()` source and declares the family `Noto Sans JP` itself, so it shadows an installed font of the same name.
- Browser support figures are from web-features 3.45.0 (2026-11-02).

## Goals / Non-Goals

**Goals:**

- Every motion in this change is declared in CSS, including its reduced-motion behaviour. TypeScript decides only what is built and where to scroll.
- A browser without a non-Baseline feature shows the content correctly, without that refinement.

**Non-Goals:**

- Changing `WINDOW_SIZE`, the growth step or the window's render cost (`meet-timetable-render-budget`).
- Route transitions other than tab switches.
- `dialog closedby` and `commandfor`; see the proposal.

## Decisions

### D1. A month jump re-opens the window at the target month

`jumpToMonth(step: 1 | -1)` finds the first date group of the month after (or before) the month of the date at the top of the screen, calls the existing `openWindow(dateKey)` (`:142`), which builds `WINDOW_CONTEXT` (2) dates above the target and fills the window below it, and then calls `scrollIntoView({ block: 'start' })` on the target group with no `behavior`, so CSS decides the motion. The dates between the old window and the target are not built; scrolling up builds them through the existing upward growth.

Right after the jump, the top edge marker is within the observer's half-screen margin, so upward growth would fire during the smooth scroll and `keepingPlace()` would write `scrollTop`, which cancels a smooth scroll. The edge observer therefore ignores entries from the jump until the scroll container's `scrollend` (with a 600 ms timeout for a browser that does not fire it), then calls the existing `reobserveEdges()` (`:239`).

Alternatives considered:
- Build every date up to the target and scroll there (the first plan). It renders up to a month of dates in one task, against the render budget, and keeps November built for no reason.
- A CSS-only jump with an anchor link to a pre-built month head. Rejected after reading the router: `<base href="/">` (`index.html:55`) turns `#m-2026-12` into `/#m-2026-12`; a full-path `href` with `data-external` bypasses the router (Aurelia docs, "Bypassing the href custom attribute"), but each jump then adds a history entry and the router re-navigates on `popstate` (`@aurelia/router` listens to `popstate` in pushState mode). The target head would also need its own rendering outside the window. More moving parts than five lines of TypeScript.
- Month sections as an exclusive accordion (`<details name>`). Rejected by the owner: only one month could be open at a time.

### D2. The buttons: one capsule, visibility from data and CSS

The two buttons sit in one capsule centred above the FAB, rendered inside `<concert-highway>` and positioned sticky at the bottom of the scroll container. Their surface follows the FAB menu items (`--md-sys-color-menu-surface`, `--shadow-soft`, 48 px targets). The icons are new `svg-icon` cases `skip-up` / `skip-down` in the existing 24 px, 2 px-stroke style (`svg-icon.html`).

- **Direction available:** on `scrollend`, the highway sets `data-has-prev` / `data-has-next` on the capsule from the loaded `dateGroups` and the date at the top of the screen; CSS hides a button whose attribute is false.
- **Only after the fan scrolls:** the scroll container is a `container-type: scroll-state` container; `@container not scroll-state(scrollable: top)` hides the capsule. A browser without scroll-state queries never matches the rule, so it shows the capsule from the start.
- **Hidden while the FAB is open:** `:root:has(.fab-panel:popover-open)` hides the capsule. No message between the components.
- **Names:** `aria-label` from new i18n keys with the target month, e.g. `dashboard.monthJump.next` = "{{month}}へ移動" / "Go to {{month}}".

### D3. Scroll motion belongs to CSS; restores pass `behavior: 'instant'`

`.concert-scroll` gets `scroll-behavior: smooth`, and `auto` under `prefers-reduced-motion: reduce`, the pattern `welcome-route.css:11` and `:405` already use. With that, every programmatic scroll in the container would animate, including the place restore in the `scrollAnchor` setter (`:311`, its `scrollIntoView()` at `:328`), whose following `scrollTop += offset` would then add to an intermediate position. The restore therefore passes `behavior: 'instant'` explicitly; that is a correctness requirement (a restore must not move), not a motion style.

### D4. The deal-in is a scroll-triggered, time-based animation

Each `.date-group` row declares its own trigger, and its three lanes run one keyframe set when the trigger activates:

```css
.date-group {
  timeline-trigger: --row view() entry 60% exit 40% / cover;
  trigger-scope: --row;
  perspective: 520px;
  perspective-origin: 70% 40%;
}
.lane {
  animation: deal-in 760ms cubic-bezier(.2, .8, .2, 1) both;
  animation-delay: calc((sibling-index() - 1) * 110ms);
  animation-trigger: --row play-forwards play-backwards;
}
@keyframes deal-in {
  0%   { opacity: 0; transform: translate3d(140px, -30px, -260px) rotateY(-75deg) rotateZ(14deg); filter: brightness(.35); }
  60%  { opacity: 1; transform: translate3d(-6px, 0, 20px) rotateY(8deg) rotateZ(-1deg); filter: brightness(1.25); }
  100% { transform: none; filter: none; }
}
```

The activation range `entry 60% exit 40%` covers a row coming in from either edge, so scrolling up after a jump deals rows in from the top. Deactivation at the end of `cover` (fully out of view) plays the animation backwards off screen, so the next entry plays again. The perspective sits on the row so the three lanes share one vanishing point.

`sibling-index()` is used only among a row's three lanes, which are always built together, so it counts 1, 2, 3. It is not used across date groups: there it counts groups already built, so every group added after the first eight would get the same delay. That miscount may also explain the removed stagger in `event-card.css:29-36` (D6).

Measured in Chromium 156 on the sample page: after a 1500 px jump, the lanes of a row in mid-screen started at 0, 90 and 180 ms (sample step) and finished at 520, 610 and 700 ms; a row entering from the top on an upward fling played forwards.

Fallback: `@supports not (timeline-trigger: --t view())` uses the same keyframes on `animation-timeline: view()`, with ranges `entry` and `exit` (reversed) so both edges animate. Under reduced motion, `animation: none` on the lanes; a scroll-driven or triggered animation has no duration token to collapse.

Alternatives considered:
- Scroll-driven only (`animation-timeline: view()`): Baseline, but its progress follows the scroll, so a fast fling finishes it at the screen edge in a few frames; the owner saw no animation in the sample.
- Time-based reveal from `@starting-style` when a group is built: the window grows half a screen ahead, so most reveals finish off screen.
- Fade-and-scale, plain slide, slide with tilt, door, flip and fly-in were sampled; the owner chose this "deal" motion.

### D5. One CSS rule stops every View Transition under reduced motion; tab switches use one

`global.css` adds, under `prefers-reduced-motion: reduce`, `animation: none` for `::view-transition-group(*)`, `::view-transition-old(*)` and `::view-transition-new(*)`. The two call sites drop their feature checks and the Discovery `matchMedia` check, and always call `document.startViewTransition`. Unit tests (jsdom has no View Transitions) stub it with a function that runs the callback at once and returns resolved promises.

Tab switches: Aurelia's router has no View Transition support (its documentation and `@aurelia/router` 2.0.0-rc.2 contain none) and the update callback must not wait for a frame (`discovery-route.ts:389`). The bottom navigation tab handler calls `document.startViewTransition(async () => { await router.load(path); runTasks() })`. The page header and the navigation bar get their own `view-transition-name`, so only the route content cross-fades. The first task is a spike that confirms `router.load()` settles without waiting for a frame; if it does not, the tab transition is dropped from this change and the app-shell requirement is revised before archive.

### D6. Find the cause of the removed stagger before building the deal-in

`event-card.css:29-36` records a staggered reveal whose rows all moved together. Before the deal-in lands, reproduce that branch in a story and check the `sibling-index()` miscount (D4) against it. If the cause is something else that also applies to triggered animations, the deal-in design is revisited.

### D7. Installed Noto through an alias family

```css
@font-face {
  font-family: "Local Noto Sans JP";
  font-weight: 100 900;
  src: local("Noto Sans JP"), local("Noto Sans CJK JP Regular");
}
--md-ref-typeface-plain:
  "Local Noto Sans JP", "Noto Sans JP", "Hiragino Sans", "Yu Gothic UI", system-ui, sans-serif;
```

Windows 10/11 ship `NotoSansJP-VF.ttf` (variable) since the April 2025 update; Android ships Noto Sans CJK JP (variable from Android 15, Regular only on 6-14, where bold is synthesized). Safari does not use `local()` for fingerprinting reasons; Apple devices have no Noto, so they download as before. The Google Fonts link stays as the fallback, and the browser fetches a Google subset only when the alias cannot draw a character. Source: ICS MEDIA, "ウェブ制作者のための Noto Sans JP 最新実装ガイド".

This edits the stack that `adopt-m3-cube-ui-foundation` introduces; the task waits for its token renames.

### D8. Japanese text and label trimming in the base layer

In `global.css` (base layer, not a block, so the block-level font ban in `stylelint.config.js` does not apply):

```css
:root {
  font-feature-settings: "palt";
  text-autospace: normal;     /* Firefox 145, Safari 27 */
  line-break: strict;
  word-break: auto-phrase;    /* Chromium; needs lang="ja", set by i18n */
}
:where(h1, h2, h3) { text-wrap: balance; }
:where(.button, .chip) { text-box: trim-both cap alphabetic; }  /* Chrome 133, Safari 18.2 */
```

`palt` and `word-break: auto-phrase` apply to body text too, by the owner's decision after viewing them; Chrome's own write-up shows `auto-phrase` on headings, and long paragraphs at 320 px may end lines with wider gaps. The Storybook stories at 320 px are checked for that and for labels that `cap alphabetic` trimming pushes too high (Japanese glyphs rise above the cap height).

### D9. Confirm dialog exit and disclosure height

The confirm dialog transitions `opacity`, `display` and `overlay` with `allow-discrete` and enters from `@starting-style`, over `--md-sys-motion-duration-short4`, which is 0 ms under reduced motion. The licenses `<details>` sets `interpolate-size: allow-keywords` and transitions `::details-content` `block-size` and `content-visibility` (`allow-discrete`); browsers without `interpolate-size` open it at once.

## Risks / Trade-offs

- [Scroll-triggered animations are Chromium-only] → Safari and Firefox get the scroll-linked fallback, which is brief on a fast scroll. Acceptable: the content is never hidden.
- [`filter: brightness()` in the deal-in is painted on the main thread] → 3 lanes per row, at most a screenful of rows at once; record a trace on the reference profile during a fling and drop the filter if frames exceed 16 ms.
- [The tab View Transition freezes the screen while the route renders] → menu-tab routes already must not block the swap on data (`bottom-nav-bar` spec); the spike measures the transition's duration on Discovery and Home.
- [Jump into a month whose first date is near the end of the data] → `openWindow` already clamps to the last window; the button state comes from the loaded dates, so it never offers a month with no dates.
- [Typeface conflict with adopt-m3] → land D7/D8 after its token renames; the plain stack is edited in one place.

## Migration Plan

Frontend only, released with the normal frontend deploy. Rollback is a revert of the PR. No data or setting changes.
