## Why

A fan who follows many artists has a Timetable that runs for months, and reaching next month means a long stretch of thumb scrolling. The Timetable also shows rows with no entrance at all: a previous staggered reveal was removed because every row moved together (`event-card.css` notes the cause was never found). Around this, the fan app uses only a few of the platform features that now make motion and Japanese text better without script: View Transitions are wrapped in feature checks and JavaScript reduced-motion checks although they are Baseline, and no stylesheet sets `palt`, `text-autospace`, `word-break: auto-phrase` or `text-box`. Noto Sans JP is always downloaded from Google Fonts, even on Windows 10/11, which has shipped it since April 2025, and on Android, which ships Noto Sans CJK JP.

## What Changes

**Timetable**

- Two month-jump buttons, in one capsule above the FAB, move the Timetable to the first date of the previous or the next month. They appear once the fan has scrolled (a `scroll-state` container query) and hide when there is no month in that direction. Their icons are "skip" glyphs (a media player's next/previous track, turned vertical).
- A jump opens the rendered window at the target month, as re-entry already does, instead of rendering every date in between. Earlier dates are rendered when the fan scrolls up, through the existing upward growth that keeps the fan's place.
- The scroll motion is set by CSS (`scroll-behavior: smooth`, `auto` under reduced motion). The position restore on re-entry and on upward growth passes `behavior: 'instant'`, so it never animates.
- When a date row comes into view, from either edge, its cards are dealt in: each card flies in from the right and back in 3D and settles with a slight overshoot, HOME, NEAR and AWAY one after another (`sibling-index()`), timed by the shared motion tokens. The animation is time-based and starts when the row enters view (scroll-triggered animations), so it is visible even during a fast scroll. Browsers without scroll-triggered animations get the same keyframes tied to scroll progress.

**Motion elsewhere**

- Switching between bottom-navigation tabs runs inside a View Transition.
- The View Transition calls in Discovery and My Artists lose their feature checks and their JavaScript reduced-motion check; one global rule stops every View Transition under reduced motion.
- The confirm dialog fades out on close (`transition-behavior: allow-discrete`). The OSS licenses' `<details>` opens and closes with a height animation (`interpolate-size`, `::details-content`).

**Japanese text**

- Windows and Android use their installed Noto (an alias `@font-face` over `local()`); other devices keep downloading Noto Sans JP from Google Fonts.
- All text uses proportional metrics (`palt`), automatic spacing between Japanese and Latin text (`text-autospace`), strict line breaking and phrase-based line breaking (`word-break: auto-phrase`). Headings use `text-wrap: balance`.
- Buttons and chips trim the line box to the cap height and baseline (`text-box`), so their labels sit in the vertical centre.

**Not changed:** the window size and growth step (owned by `meet-timetable-render-budget`), the bottom sheet's open and close, `dialog closedby` (Safari does not support it, so the JavaScript backdrop check would stay; adopt it when Safari ships it), `commandfor` (dialogs and sheets are opened from view-model state), and canvas motion (`dna-orb`, `celebration-overlay`), which CSS cannot stop.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `components/infrastructure/fan/web/route/dashboard`: adds the month-jump buttons; the window requirement gains the jump as a third place the window can start.
- `components/infrastructure/fan/web/global/live-highway`: adds the dealt-in entrance of date rows.
- `components/infrastructure/fan/web/global/app-shell`: "Page Transition Animations" is removed and replaced by "Tab switches cross-fade". The removed requirement asks every route change to fade and slide, but no route transition is implemented today (`app-shell.html` has a plain `<au-viewport>`; the only View Transitions are the in-place edits in Discovery and My Artists). The new one covers what this change delivers, tab switches.
- `components/infrastructure/fan/web/global/design-tokens`: adds the Japanese text settings, the label trimming, and the use of installed Noto.
- `components/infrastructure/fan/web/global/ui-primitives`: adds the confirm dialog's exit and the disclosure height animation.

## Impact

- **frontend only.** `src/components/live-highway/` (concert-highway, event-card), `src/routes/dashboard/`, `src/components/bottom-nav-bar/`, `src/routes/discovery/discovery-route.ts`, `src/routes/my-artists/my-artists-route.ts`, `src/components/confirm-dialog/`, `src/routes/legal/licenses-route.css`, `src/components/svg-icon/` (two icons), `src/styles/global.css`, `shared/styles/m3-sys.css` (typeface stack), and both locale files.
- **No API, proto, backend or infrastructure change.** `font-src` already allows `fonts.gstatic.com`; `local()` needs no CSP change.
- **Browser support** (web-features 3.45.0, 2026-11-02): View Transitions, `sibling-index()`, `@starting-style`, `transition-behavior`, `::details-content` and scroll-driven animations are Baseline. Scroll-triggered animations, `scroll-state` queries, `interpolate-size` and `word-break: auto-phrase` are Chromium-only; `text-autospace` is Firefox and Safari only; `text-box` is Chrome and Safari. Each is used so that a browser without it shows the content without that refinement.
- **Concurrent work.** `adopt-m3-cube-ui-foundation` changes the same typeface stack (`m3-sys.css`, `index.html`) and the live-highway layout requirement; the typography tasks land after its token renames. `meet-timetable-render-budget` owns the window size; the reveal and the jump must stay inside its render bounds.
