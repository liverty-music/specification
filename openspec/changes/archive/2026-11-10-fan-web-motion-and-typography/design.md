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

`jumpToMonth(step: 1 | -1)` finds the first date group of the month after (or before) the month of the date at the top of the screen, calls the existing `openWindow(dateKey)` (`:142`), which builds `WINDOW_CONTEXT` (2) dates above the target and fills the window below it. `openWindow()` replaces the built groups without touching `scrollTop`, so the scroll position after it is arbitrary relative to the target. The jump therefore first places the view instantly (`behavior: 'instant'`) a little before the target in the jump's direction: for the next month at the top of the built content, which shows the two context dates above the target; for the previous month two date groups below the target. It then calls `scrollIntoView({ block: 'start' })` on the target with no `behavior`, so CSS animates a short final scroll that runs in the jump's direction. The dates between the old window and the target are not built; scrolling up builds them through the existing upward growth.

Right after the jump, the top edge marker is within the observer's half-screen margin, so upward growth would fire during the smooth scroll and `keepingPlace()` would write `scrollTop`, which cancels a smooth scroll. The edge observer therefore ignores entries from the jump until the scroll container's `scrollend` (with a 600 ms timeout for a browser that does not fire it), then calls the existing `reobserveEdges()` (`:239`).

Alternatives considered:
- Build every date up to the target and scroll there (the first plan). It renders up to a month of dates in one task, against the render budget, and keeps November built for no reason.
- A CSS-only jump with an anchor link to a pre-built month head. Rejected after reading the router: `<base href="/">` (`index.html:55`) turns `#m-2026-12` into `/#m-2026-12`; a full-path `href` with `data-external` bypasses the router (Aurelia docs, "Bypassing the href custom attribute"), but each jump then adds a history entry and the router re-navigates on `popstate` (`@aurelia/router` listens to `popstate` in pushState mode). The target head would also need its own rendering outside the window. More moving parts than five lines of TypeScript.
- Month sections as an exclusive accordion (`<details name>`). Rejected by the owner: only one month could be open at a time.

### D2. The buttons: one capsule, visibility from data and CSS

The two buttons sit in one capsule centred above the FAB, rendered inside `<concert-highway>` and positioned sticky at the bottom of the scroll container. Their surface follows the FAB menu items (`--md-sys-color-menu-surface`, `--shadow-soft`, 48 px targets). The icons are new `svg-icon` cases `skip-up` / `skip-down` in the existing 24 px, 2 px-stroke style (`svg-icon.html`).

- **Direction available:** the highway sets `data-has-prev` / `data-has-next` on the capsule from the loaded `dateGroups` and the date at the top of the screen when a window opens (first display, re-entry, jump, a replaced list) and on each `scrollend`; CSS hides a button whose attribute is false. This rule applies in every browser and wins over the visibility rule below.
- **Only after the fan scrolls:** the scroll container is a `container-type: scroll-state` container; `@container not scroll-state(scrollable: top)` hides the capsule. A browser without scroll-state queries never matches the rule, so it shows the capsule from the start, with each button still following its direction attribute.
- **Hidden while the FAB is open:** `:root:has(.fab-panel:popover-open)` hides the capsule. No message between the components.
- **Names:** `aria-label` from new i18n keys with the target month, e.g. `dashboard.monthJump.next` = "{{month}}へ移動" / "Go to {{month}}".

### D3. Scroll motion belongs to CSS; restores pass `behavior: 'instant'`

`.concert-scroll` gets `scroll-behavior: smooth`, and `auto` under `prefers-reduced-motion: reduce`, the pattern `welcome-route.css:11` and `:405` already use. With that, every programmatic scroll in the container would animate, including the place restore in the `scrollAnchor` setter (`:311`, its `scrollIntoView()` at `:328`), whose following `scrollTop += offset` would then add to an intermediate position. The restore therefore passes `behavior: 'instant'` explicitly; that is a correctness requirement (a restore must not move), not a motion style.

### D4. The deal-in is a scroll-triggered, time-based animation

Each `.date-group` row declares its own trigger, and its concert cards run one keyframe set when the trigger activates. The animation is on the cards (`.lane > event-card`), not on the lanes: the owner's check in production found the lanes' frames and the empty-lane mark moving with them, and asked for the cards alone, with the cards of one lane in order from the top. Each card's delay is `(lane step + sibling-index() - 1) × short2`, where the lane step (0, 1, 2 for HOME, NEAR, AWAY) is a custom property set from the lane's `data-lane`, and `sibling-index()` counts the cards of one lane. The sketch below is the first version, on the lanes:

```css
.date-group {
  timeline-trigger: --row view() entry 60% exit 40% / cover;
  trigger-scope: --row;
  perspective: 520px;
  perspective-origin: 70% 40%;
}
.lane {
  animation: deal-in var(--md-sys-motion-duration-extra-long2) var(--md-sys-motion-easing-emphasized-decelerate) both;
  animation-delay: calc((sibling-index() - 1) * var(--md-sys-motion-duration-short2));
  animation-trigger: --row play-forwards play-backwards;
}
@keyframes deal-in {
  0%   { opacity: 0; transform: translate3d(140px, -30px, -260px) rotateY(-75deg) rotateZ(14deg); filter: brightness(.35); }
  60%  { opacity: 1; transform: translate3d(-6px, 0, 20px) rotateY(8deg) rotateZ(-1deg); filter: brightness(1.25); }
  100% { transform: none; filter: none; }
}
```

The activation range `entry 60% exit 40%` covers a row coming in from either edge, so scrolling up after a jump deals rows in from the top. Deactivation at the end of `cover` (fully out of view) plays the animation backwards off screen, so the next entry plays again. The perspective sits on the row so the three lanes share one vanishing point.

In the first version `sibling-index()` was used only among a row's three lanes, which are always built together, so it counted 1, 2, 3; since task 4.3 it counts the cards of one lane, which are built together too. It is not used across date groups: there it counts groups already built, so every group added after the first eight would get the same delay. That miscount may also explain the removed stagger in `event-card.css:29-36` (D6).

Durations come from the motion tokens (design-tokens, "Scattered raw timings are consolidated"): extra-long2 (800 ms) for the deal-in, short2 (100 ms) for the step between lanes, and the emphasized-decelerate curve; the overshoot is in the keyframes. The owner chose the motion on a sample run at 760 ms with a 110 ms step; the token values are the nearest on the scale.

Measured in Chromium 156 on an earlier version of the sample (520 ms duration, 90 ms step, before the 3D keyframes): after a 1500 px jump, the lanes of a row in mid-screen started at 0, 90 and 180 ms and finished at 520, 610 and 700 ms, so the trigger fired once per row and the `sibling-index()` delay applied; a row entering from the top on an upward fling played forwards.

Fallback: `@supports not (timeline-trigger: --t view())` uses the same keyframes on `animation-timeline: view()`, with ranges `entry` and `exit` (reversed) so both edges animate. Both edges need two animations of the same keyframes on one element, because one animation has one range. The sketch is the first version, on the lanes; since task 4.3 the same rule selects `.lane > event-card` and takes `--_lag` from the lane step (`var(--_lane-step) * 12%`):

```css
@supports not (timeline-trigger: --t view()) {
  .lane {
    --_lag: calc((sibling-index() - 1) * 12%);
    /* The exit animation fills forwards only: with `both`, its backwards fill
       (keyframe 100%, no transform) would override the entry animation, which
       comes earlier in the list, for the whole time the row is in view. */
    animation: deal-in linear both, deal-in linear forwards reverse;
    animation-timeline: view(), view();
    animation-range:
      entry var(--_lag) entry calc(60% + var(--_lag)),
      exit 40% exit 100%;
  }
}
```

A scroll-linked animation ignores `animation-delay`. Each card follows its own view progress, so the cards of a lane come in from the top down as they reach the view, and the lane order (HOME, NEAR, AWAY) comes from the `--_lag` offset on each entry range. The exit range has no offset: each card starts to leave once 40% of it has gone through the top edge, so no card flies out while most of it is still on screen. (In the first version the lanes shared the row's view progress, and every lane left once 40% of the row had gone.) Unlike the triggered path, whose reverse play happens off screen, the fallback's exit is visible; the live-highway requirement states it, and the owner accepted it in the samples ("上端でも動かす"). The sample page ran this form in Chromium with scroll-triggered animations switched off by mode. Under reduced motion no deal-in is declared at all: both paths sit inside `@media (prefers-reduced-motion: no-preference)`, because a scroll-driven or triggered animation has no duration token to collapse.

Alternatives considered:
- Scroll-driven only (`animation-timeline: view()`): Baseline, but its progress follows the scroll, so a fast fling finishes it at the screen edge in a few frames; the owner saw no animation in the sample.
- Time-based reveal from `@starting-style` when a group is built: the window grows half a screen ahead, so most reveals finish off screen.
- Fade-and-scale, plain slide, slide with tilt, door, flip and fly-in were sampled; the owner chose this "deal" motion.

### D5. One CSS rule stops every View Transition under reduced motion; tab switches use one

`global.css` adds, under `prefers-reduced-motion: reduce`, `animation: none` for `::view-transition-group(*)`, `::view-transition-old(*)` and `::view-transition-new(*)`. The two call sites drop their feature checks and the Discovery `matchMedia` check, and always call `document.startViewTransition`. Unit tests (jsdom has no View Transitions) stub it with a function that runs the callback at once and returns resolved promises.

Tab switches: Aurelia's router has no View Transition support (its documentation and `@aurelia/router` 2.0.0-rc.2 contain none) and the update callback must not wait for a frame (`discovery-route.ts:389`). The bottom navigation tab handler calls `document.startViewTransition(async () => { await router.load(path); runTasks() })`. The page header and the navigation bar get their own `view-transition-name`, so only the route content cross-fades. The first task is a spike that confirms `router.load()` settles without waiting for a frame; if it does not, the tab transition is dropped from this change and the app-shell requirement is revised before archive.

Spike result (task 1.2, Chromium of Playwright 1.64.1, local dev server): `router.load()` settles inside the update callback. Home → My Artists → Discovery → Home each ran one transition whose `ready` and `finished` resolved, with no `TimeoutError`. Implementation notes from the spike:

- The handler is bound with `click.capture` on the tab link and stops the event, so the router's own `href` click handler on the same link does not navigate a second time. The link keeps the router's URL (`href.bind`) for a modified or middle click, which the handler leaves alone. `data-external` was tried first and rejected: it makes the router write the raw relative path into `href`.
- A named snapshot is painted above `root`, so the FAB, which overlaps the navigation bar, is named on every transition (`fab-toggle`), not only under `vt-suppress-root`.
- The old snapshots of the bar, the header and the FAB are hidden (`opacity: 0`, no animation): the header's background is partly transparent and would show the old title through the new one.
- A `*` argument adds no specificity, so the reduced-motion rule is written `:root::view-transition-old(*)` (and `-new`, `-group`) to win over the named rules (`root`, `discovery-view`).
- The `root` fade uses `--md-sys-motion-duration-medium2` (300 ms) to meet the requirement's 250-350 ms; it used `short4` (200 ms) when it served no transition.

### D6. Find the cause of the removed stagger before building the deal-in

`event-card.css:29-36` records a staggered reveal whose rows all moved together. Before the deal-in lands, reproduce that branch in a story and check the `sibling-index()` miscount (D4) against it. If the cause is something else that also applies to triggered animations, the deal-in design is revisited.

Spike result (task 1.1, Chromium of Playwright 1.64.1): the removed CSS (commit `470dda3e`: an `opacity`/`translate` transition from `@starting-style` on `.date-group`, `transition-delay: min(calc(sibling-index() * 60ms), 400ms)`) was injected into a `concert-highway` story of the current component and sampled every frame. On the first window it staggers as written: every row's transition has the same start time, the delays compute to 120, 180, 240 … ms (the top edge marker is sibling 1), and the rows' opacities at one instant read 0.72, 0.55, 0.35, 0.13. So the report "every row moved together" does not reproduce on today's component, and the `sibling-index()` count does not explain it for the rows on screen. The count does go wrong for rows added while scrolling: they are siblings 14 and above, and every one of them got the 400 ms cap, so a grown window's rows would move together. The original failure was measured on the component before the date window (every row built, `content-visibility: auto`, a scroll-driven reveal on the same element), which is gone; the cause on that component is not recoverable from here and no longer matters.

The deal-in does not share either cause: it starts from a scroll trigger, not from insertion (`@starting-style`), and `sibling-index()` counts only the cards of one lane. The `DealIn` story checks it on a grown window: a row added by scrolling, with two HOME, one NEAR and two AWAY cards, runs its cards at 0/100, 100 and 200/300 ms for 800 ms, like a row of the first window, and settles at full opacity with no transform.

Implementation notes (task 4.1):

- The perspective is on `.lane-grid`, the lanes' parent, not on `.date-group`: `perspective` applies to an element's children, and the lanes are the row's grandchildren. Since the deal-in moved to the cards (task 4.3), the cards are `.lane-grid`'s grandchildren, so each lane keeps the 3D space (`transform-style: preserve-3d`); without it the cards turned flat (the `DealIn` story measures a card's box at the first frame against a flat lane).
- The exit action is `reset`, not `play-backwards` (`animation-trigger: --row play-forwards reset`). With `play-backwards`, a row scrolled fully out and back within the 800 ms resumed from where the backward play had reached (the E2E test "A row comes back" measured a lane at 866 ms of 1000 right after re-entry), so it was not dealt in again. `reset` returns the animation to its start once the row has left, which is what the requirement asks.
- The `filter: brightness()` in the keyframes is dropped (task 4.2). Measured with Playwright's Chromium, headless on the development machine (WSL, no GPU), with 4× CPU throttling and a 1.5 s wheel fling on `/dashboard`, three runs each: with the filter the median frame was 33 ms and 72-84 frames exceeded 33 ms; without it the median was 16.8 ms and 68-77 exceeded 33 ms; with no deal-in at all, 10-26 frames exceeded 33 ms. Frames over 16 ms occur in this environment even without the deal-in, so the task's 16 ms rule was applied as "the filter adds frame time, drop it". The deal-in itself still adds long frames here; a software-rendered headless browser exaggerates 3D transforms, so the owner's device check (task 8.1) is the measure that counts, and if it stutters there the next step is to reduce the 3D part of the keyframes.
- Rows out of view hold the opening keyframe (`both`), so a test that measures where a lane or a card is reads layout boxes (`offsetLeft` up the offset-parent chain) or waits for the rows in view to settle; the `concert-highway` stories do.

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

Only variable local fonts may match. Within one family the browser picks the nearest weight face and never falls through to the next family, so a Regular-only local face would draw bold text at 400 (`font-synthesis-weight: none` in `global.css`). A device without a variable Noto gets no local face and downloads "Noto Sans JP", the next family. The `@font-face` sits in `shared/styles/m3-sys.css` beside the plain stack, so the organizer console uses it too. Safari does not use `local()` for fonts it does not ship; Apple devices have no Noto, so they download as before. The Google Fonts link stays as the fallback. Source: ICS MEDIA, "ウェブ制作者のための Noto Sans JP 最新実装ガイド".

**Names (task 1.3).** `local()` matches a font's full name (name ID 4) or PostScript name (name ID 6). Read from the font files' name tables rather than on devices: the Android files from AOSP `platform/external/noto-fonts` (`notosanscjk/`), the Windows file from a Windows 11 `C:\Windows\Fonts`, the static files from Google's noto-cjk releases.

| Font | Full name | PostScript name | Weights |
|---|---|---|---|
| Windows 10/11 `NotoSansJP-VF.ttf` | `Noto Sans JP` | `NotoSansJP-Thin` | variable 100-900 |
| Android 15+ `NotoSansCJK-wght-400-900.otf.ttc` | `Noto Sans CJK JP Regular` | `NotoSansCJKJP-Regular` | variable 400-900 |
| Android 6-14 `NotoSansCJK-Regular.ttc` | `Noto Sans CJK JP` | `NotoSansCJKjp-Regular` | Regular only |
| Static Noto Sans JP Regular, installed by hand | `Noto Sans JP` | `NotoSansJP-Regular` | 400 only |
| Linux `fonts-noto-cjk` (static) | `Noto Sans CJK JP` (Regular) | `NotoSansCJKjp-Regular` | one weight per file |

So `local("Noto Sans JP")` matches Windows' own font and `local("Noto Sans CJK JP Regular")` only Android 15's variable file; the name the earlier draft used, `Noto Sans CJK JP`, is the full name of Android 14's Regular-only file and of the Linux static Regular, and would have drawn bold at 400 there. PostScript names are avoided: `local()` compares them case-insensitively, and the variable file's `NotoSansJP-Thin` is also the static Thin's name. A static Noto Sans JP Regular installed by hand still answers to "Noto Sans JP"; that case stays outside the requirement's guarantee. Android 15's variable file starts at 400, so the requirement states 400-900 for it; the app uses no weight below 400. Whether Chrome on Android resolves the full name as read from the file is confirmed on the owner's device in task 8.1.

@spec-manual components/infrastructure/fan/web/global/design-tokens "Android 15 or later" -- no Android device in CI; verified by the owner in production on 2026-11-10 (v1.153.0, task 8.1) on an Android 15-or-later device: Chrome's network panel showed no Noto Sans JP file.

@spec-manual components/infrastructure/fan/web/global/design-tokens "Android 14 or earlier" -- no Android device in CI; the names above show that no `local()` source matches Android 14's Regular-only file, and the Chromium download path is the same one `e2e/functional/local-noto.spec.ts` "iPhone" checks on a machine without a variable Noto; not run on an Android 14 device or emulator.

### D8. Japanese text in the base layer

In `global.css` (global layer, not a block, so the block-level font ban in `stylelint.config.js` does not apply):

```css
:where(html) {
  font-feature-settings: "palt";
  text-autospace: normal;     /* Firefox 145, Safari 27 */
  line-break: strict;
  word-break: auto-phrase;    /* Chromium; needs lang="ja", set by i18n */
}
```

Headings already balance their lines in `shared/styles/reset.css`.

`palt` and `word-break: auto-phrase` apply to body text too, by the owner's decision after viewing them; Chrome's own write-up shows `auto-phrase` on headings, and long paragraphs at 320 px may end lines with wider gaps. The Storybook stories at 320 px are checked for that.

**Type styles as longhands.** The `font` shorthand resets every font property it does not name, `font-feature-settings` among them, so each of the 30 `.md-typescale-*` classes, the button and the body rule set `palt` back to `normal` on everything that had a type style. Rather than repeat `palt` beside each shorthand, the type style tokens in `shared/styles/m3-sys.css` become separate tokens per property, as Material Web names them (`--md-sys-typescale-<style>-font`, `-weight`, `-emphasized-weight`, `-size`, `-line-height`, `-tracking`), and every consumer sets the longhands. The classes then set five declarations, which `stylelint.config.js` allows for `m3-typescale.css` alone. The button's `--button-font` hook becomes `--button-font-size` and `--button-line-height` (the typeface and weight stay shared). The banners and the event card's artist name, the documented exceptions to type styles, keep their own sizes as longhands. The organizer console uses the same tokens, so it changes in the same way; it sets no `palt`, so it renders as before. This replaces the token shape `adopt-m3-cube-ui-foundation`'s design gives (one `font` value per type style, two declarations per class); that change's design is not edited here because it is in progress in the same working tree.

**Label trimming is not in this change.** `text-box: trim-both cap alphabetic` on `.button` and `.chip` did not reach the label: the label is bare text in an `inline-flex` box, an anonymous flex item no selector reaches (w3c/csswg-drafts#14514), and the space above the capitals stayed 18 px against 16 px below the baseline. The fix is a label element in about 85 templates, so it moves with the "Labels sit in the vertical centre of their controls" requirement to its own change: liverty-music/specification#1371.

### D9. Confirm dialog exit and disclosure height

The confirm dialog transitions `opacity`, `display` and `overlay` with `allow-discrete` and enters from `@starting-style`, over `--md-sys-motion-duration-short4`, which is 0 ms under reduced motion. The licenses `<details>` sets `interpolate-size: allow-keywords` and transitions `::details-content` `block-size` and `content-visibility` (`allow-discrete`); browsers without `interpolate-size` open it at once.

## Risks / Trade-offs

- [Scroll-triggered animations are Chromium-only] → Safari and Firefox get the scroll-linked fallback, which is brief on a fast scroll. Acceptable: the content is never hidden.
- [`filter: brightness()` in the deal-in is painted on the main thread] → 3 lanes per row, at most a screenful of rows at once; record a trace on the reference profile during a fling and drop the filter if frames exceed 16 ms.
- [The tab View Transition freezes the screen while the route renders] → menu-tab routes already must not block the swap on data (`bottom-nav-bar` spec); the spike measures the transition's duration on Discovery and Home.
- [Jump into a month whose first date is near the end of the data] → `openWindow` already clamps to the last window; the button state comes from the loaded dates, so it never offers a month with no dates.
- [Without the feature checks, `document.startViewTransition` throws in a browser older than View Transitions (Safari before 18, Firefox before 144), so the unfollow, the Discovery swap and tab switches fail there] → accepted by the owner: View Transitions are Baseline since 2025-10-14, and the fan app targets current browsers. If support for older browsers becomes a goal, the checks return in one helper, not at each call site.
- [A static Noto Sans JP Regular installed by hand answers to `local("Noto Sans JP")`, so bold may draw at 400 there] → outside the requirement's guarantee, which covers Windows' and Android's own variable fonts; Linux's `fonts-noto-cjk` and Android 14's Regular-only file do not match (D7).
- [Typeface conflict with adopt-m3] → land D7/D8 after its token renames; the plain stack is edited in one place.

## Migration Plan

Frontend only, released with the normal frontend deploy. Rollback is a revert of the PR. No data or setting changes.
