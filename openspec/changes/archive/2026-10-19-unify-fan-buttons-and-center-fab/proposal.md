## Why

The fan app's bottom edge does not read as one designed surface. The update snack bar floats about 72px above the bottom navigation because a rule matches the install banner's host element even when the banner is hidden. Its 「更新」 action looks like body text, against the snack-bar spec, because an earlier restyle (frontend PR #603) bypassed the spec. The FAB sits in the bottom-right corner, where it covers the AWAY lane (the busiest timetable column) and is a stretch for the right thumb. Its `+` glyph says "add", not "open actions", and the FAB stays in its open state after the fan navigates away and back. Underneath all of this, the app has no shared button: 44 page-specific button classes each restate a primary, secondary or ghost look.

## What Changes

- Every snack bar sits `space-s` above the bottom navigation, plus the measured height of a visible bottom banner (the same value the FAB already uses). The per-banner fixed clearances are removed.
- A single button style with four variants: **filled** (the default), **outlined** (it also takes the former text and ghost buttons), **danger**, and **on-container** (a translucent fill with a white border, for buttons on a coloured surface such as a snack bar). All corners use `--radius-button`. The 44 page-specific button classes move onto it. A Storybook catalog story pins the look with a screenshot test.
- The update snack bar's action uses the on-container variant. It glows three times when the snack bar appears, then stays still.
- **BREAKING (navigation)**: the bottom navigation has four tabs (Home, Discover, My Artists, Tickets). Settings leaves the bar and opens from a gear in the page header of each of those four tab pages.
- The FAB moves to the centre of the bottom navigation and protrudes from a notch cut into the bar. The bar keeps the centre slot on every route, so the four tabs never move. On routes without FAB actions (Tickets, Event, order detail and others), the slot is empty and the bar has no notch.
- Tapping the FAB unfolds its actions one after another along a tall arc that follows the right thumb's sweep, starting at the FAB and curving up and to the right. Left-handed mode mirrors the arc to the left.
- While a snack bar is open, the FAB sinks into the notch and gets smaller, so the snack bar can sit directly above the navigation. The FAB stays tappable.
- While the signup prompt or the install banner is visible, the FAB floats just above the banner instead and the bar shows no notch, so the FAB covers no part of the banner. This is a stopgap until those banners become snack bars (a separate change).
- The FAB glyph becomes a 32px equalizer (three bars). It turns into `×` when the FAB opens; the bars bounce only at that moment.
- After the fan navigates away and back, the FAB always shows its collapsed state.
- An e2e test checks that the FAB stays in the top layer and receives taps above the Discovery dna orb.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `components/infrastructure/fan/web/global/snack-bar`: placement above the navigation and a visible banner; the update action's look and glow; the entry and exit motion direction now match the up-from-bottom placement.
- `components/infrastructure/fan/web/global/fab-menu`: centre placement in the notch, the thumb-arc unfold, the equalizer glyph, the sink while a snack bar is open, the collapsed state after navigation, the top-layer guarantee on Discovery, and left-handed mode mirroring the arc instead of the corner.
- `components/infrastructure/fan/web/global/bottom-nav-bar`: four tabs with a centre notch for the FAB; the Settings route highlights no tab.
- `components/infrastructure/fan/web/global/page-header`: a Settings entry on the four tab pages.
- `components/infrastructure/fan/web/route/settings`: the header label no longer refers to a Settings tab.
- `components/infrastructure/fan/web/global/ui-primitives`: the shared button style and its four variants.

## Impact

- **frontend only.** No proto, backend or infrastructure change.
- Styles: a new `src/styles/button.css` (block and exception layers), `main.css` import, `global.css` (the banner-clearance rules go, a snack-open flag comes), `shared/ui/snack-bar/snack-bar.css` and `.html`, `src/components/fab-menu/*`, `src/components/bottom-nav-bar/*`, `src/components/page-header/*`, `tokens.css` (FAB tokens).
- Routing: `src/app-shell.ts` (Settings `nav: false`).
- Button migration: about 25 templates and their CSS under `src/routes/**` and `src/components/**`.
- i18n: `settings.leftHandedDesc` (ja, en) and a label for the header Settings entry.
- Tests: the button catalog story with a screenshot, a snack-bar update-action story, fab-menu unit tests, the existing e2e `fab-menu-beam-toggle.spec.ts` (placement scenario), new e2e for the top layer on Discovery, and the bottom-nav and page-header stories and screenshots.
- The coach mark's tab targets (`data-nav="home"`, `data-nav="my-artists"`) are kept; the bottom-nav spec named them `data-nav-dashboard` / `data-nav-my-artists`, which the code never used, and is corrected.
