## Context

The fan web app (frontend) already uses M3 tokens for colour roles, shape, state layers, type styles and motion easing. What differs from the guideline is mostly behaviour: how screens change, what shows while data loads, and a few control details. See proposal.md for the motivation.

The findings come from a static reading of the code (frontend `main` at `3e0cc066`) against the M3 snapshot used by the `m3-design` skill, then checked by a second model and by hand. Every finding is in `audit-items.md`, grouped by theme (`T1`…`T13` adopt, `T10` measure first, `K*` decided). Limits of the audit that tasks must cover:

- Only static code was read. Nothing was measured on a device.
- The concert sheet was covered thinly (43 of 78 rules could not be judged from code).
- Surfaces with no M3 counterpart (artist bubbles canvas, orb, confetti, virtual ticket flip and stamp, celebration) were not audited.
- Colour contrast was partly computed by hand.

The dev environment is stopped, so nothing here is verified on dev: unit and component tests, visual baselines, Playwright against a local build, and read-only checks on prod after merge.

## Goals / Non-Goals

**Goals:**
- Screen changes, loading and state feedback follow the M3 patterns named in the specs.
- Every adopt finding in `audit-items.md` is fixed, or a task records why it was not (a measured result, or a spec reason that holds).
- The motion costs nothing when nothing animates, and stays within the app's existing animation budget on low-end phones.

**Non-Goals:**
- Brand colours, shapes, typefaces and shadows (M3 allows customising them), the celebration and virtual-ticket effects, and wide-screen layouts.
- A new animation library. Motion uses CSS and the browser's View Transition support the app already uses.

## Decisions

The owner approved every decision below ("全て賛成", 2026-11-23) on the audit report.

**D1. A tab switch is a top-level change; it is no longer a cross-fade.** M3: "The exiting screen quickly fades out and then the entering screen fades in", and "Fully fade out content before fading new content in" (`styles__motion__transitions.md`, Top level and Clean fades). The measured samples last 100–133 ms in total. The spec says 200 ms or less. Alternative: keep the 300 ms simultaneous fade (rejected: the two screens overlap at half opacity, which the guideline calls messy).

**D2. Forward and backward changes get a fade, not a slide.** The guideline's Android default is a fade (the screens do not travel the full width); the iOS parallax slide is the other default. A slide would also tell the fan they can swipe between screens, which the app does not support on these routes. The spec says 500 ms or less (the measured Android sample is 467 ms). A directional slide may be added later if the owner wants more motion; it needs its own spec change.

**D3. Reduced motion keeps a short fade (100 ms or less) and stops movement.** M3: "subtle fades instead of intense sliding". Decorative loops (shimmer, pulsing, spinning decoration) stop. Alternative: stay instant (rejected: an instant swap is a jump cut, which the guideline lists as jarring). On 2026-11-25 the owner confirmed amending the living specs that made reduced motion instant (snack-bar, signup-prompt-banner, pwa-install-banner, celebration-overlay, home-area-selector) rather than closing those findings. Mechanism: the duration tokens that drive movement stay 0 ms under reduced motion; the effects springs (opacity only) keep 100 ms; a surface that would move fades with `--md-sys-motion-duration-reduced-fade` (100 ms), which reduced motion does not collapse. A disclosure and an in-place list edit still change at once.

**D4. The toggle switch becomes 52 × 32 px with a handle that grows on press; this is a stated exception to "no control scales when pressed".** The numbers (track 52 × 32, handle 16 unselected, 20 default, 24 selected, 28 pressed) are the M3 switch tokens (`tokens/md-comp-switch.md`). With the current 44 × 24 track a 28 px handle would not fit, so size and press behaviour are decided together. The activation target stays as the Settings spec states (at least 24 px on both axes, with the adjacent disclosure control as the larger neighbouring target); the larger track already meets it.

**D5. A snack with an action stays 10 s, and its timer pauses while the fan hovers or focuses it.** M3 says action snackbars should not auto-dismiss. The project's snack-bar spec sets 10 s for a snack with an action (the Snack Bar Component requirement), and a snack that never leaves would stay over the bottom navigation on a phone; the owner kept 10 s. Pausing while the fan is interacting removes the real harm (the snack leaving while it is being read or used).

**D6. The snack's severity icon stays.** It tells the severity without colour. M3 does not forbid it.

**D7. The date tabs are treated as a segmented button, not as tabs.** They select one of a few dates in place and do not switch content areas. This settles `K8` findings about tab placement and indicators; those findings are then checked against the segmented-button guidance instead.

**D8. Japanese text takes the medium language height.** M3: "default to medium language height… switch to other sizes based on detected language", and ignoring it risks overlapping text. The medium value of every style is in the design-tokens tables of both apps; they are the Material 3 `md.ref.typeface.<style>.line-height` tokens, Language height = Medium, Web (m3-design snapshot 2026-11-19, token data). The earlier "about 7% taller" estimate was wrong and is not used.

**D9. The bottom sheet's scrim stays non-dismissable, and wide-screen rails wait.** The bottom-sheet spec requires the scrim not to close the sheet, to stop accidental loss of a half-filled form. Wide screens are not the fan app's use (phone first).

**D10. Japanese line height is verified by a Japanese run of every story, with baselines for a few.** A visual baseline of every screen in Japanese would add dozens of images that fail on font rendering as much as on layout, and the risk is text cut off, which an automated check finds. The `storybook-ja` Vitest project runs every story with the document in Japanese and applies the existing fits-screen and accessibility checks; a story tagged `japanese` also keeps a baseline of its own (`<name>-ja`), chosen among the rows and placeholders whose text is densest; a story tagged `latin-metrics` asserts the pixel size of Latin text and is skipped there. Task 5.2's "visual baseline of every fan screen and every console screen" is met this way (owner agreed, 2026-11-24).

**D11. A skeleton's size is measured on three screens and approximated on the rest.** The skeleton takes the room of what replaces it, so each screen's placeholder is sized from its loaded content. A Playwright check (`e2e/functional/loading-layout.spec.ts`) holds a screen's data back, measures the skeleton and the loaded content and fails when they differ: notifications (168 px a row), the concert page (640 px of 642 px) and a ticket event with one ticket (717 px). The other screens (passkeys, lottery and resale entries, order, checkout, the entry forms) take the shared sizes of `state-placeholder` (a list item 72 px, a card 128 px, overridable by `--skeleton-row-block-size`): their loaded height follows the data (the number of entries, the steps of a form), so one measured value would be right for one fixture only. The visual baseline of a skeleton is not taken: its shimmer animates (the Storybook rule for animated elements), and the story `LoadingShapes` asserts the sizes of its rows instead. Task 2.3's "per screen" is met this way (owner agreed, 2026-11-24).

**How the motion is built.** Screen changes go through the app's existing route-transition hooks, which already use the browser's View Transitions; the change adds a per-navigation kind (tab switch, forward, back) so the right pattern runs. Enter and exit motion uses CSS (`@starting-style` and `transition-behavior: allow-discrete`) for elements that are shown and removed, with durations and easing taken from the motion tokens (no raw milliseconds). Skeletons are one shared presentational piece in the shared styles, reused by each screen, so a screen declares only what its placeholder looks like. Press and selected feedback stays in stylesheets keyed off state, in line with the existing "no per-control work" rule in the app-shell spec.

**Findings that need the spec's reason first.** Adopt findings that conflict with a living requirement outside this change's deltas: `dialogs#n2`, `dialogs#n4` (post-signup dialog steps), `fab-and-action-menu#n2`, `fab-and-action-menu#n6` (action menu order and behaviour), `discovery-chrome#n13` (discovery reduced motion), `welcome-onboarding-celebration#n0` (welcome reduced motion), `snackbar#n8` (snack-bar spec: no transition under reduced motion, and a swiped snack leaves without exit motion) and `banners-and-feedback#n10` (signup-prompt-banner and pwa-install-banner: appear instantly under reduced motion). Apply reads each requirement's rationale first. If M3 still serves the fan better, the spec is amended through `/opsx:update` before the code changes; if the rationale holds, the task is closed with the reason written beside it.

## Risks / Trade-offs

- [A new top-level transition adds a View Transition on every tab tap, which could cost frames on low-end phones] → measure on the Android test device before and after; the 200 ms ceiling and a fade-only transition keep the cost low. If it drops frames, fall back to an opacity-only CSS fade without View Transitions.
- [Skeletons that do not match the loaded layout make the page jump when content arrives, which is worse than the loading text] → each skeleton takes the exact size of the loaded rows; a visual baseline compares the two states.
- [Medium line height changes every Japanese screen's height, and the type styles are shared with the organizer console, so the console gets the same change and can push content off screen or break fixed-height components] → apply the token change, then check each screen with the visual baselines and the audit's text-size and long-string findings (`T13`) in the same pass.
- [The audit was static, so some findings may not reproduce] → each fix task starts by reproducing the finding on the local build; a finding that does not reproduce is closed with that note, not changed.
- [Reduced-motion fades are new motion for people who asked for less] → they are 100 ms or less and have no movement, as M3 states.

## Open Questions

- Whether the navigation bar's selected icon should be a filled version (`K10`) and how switch and nav-bar feedback should look beyond the switch. The owner has not chosen; section 3 treats the nav-bar icon as a decision to take on a prototype on the Android test device, not as a task to implement now.

**`my-artists#n6` is answered by naming each radio, not by a radiogroup (2026-11-25).** The hype radios of an artist sit in four cells of a table row, so a `radiogroup` container would have to replace the row and break the table's semantics. Each radio is already named "artist, level" (`hype-dot-radio.ts`), and the row header names the row, so a screen reader hears whose level each radio sets.

**`discovery-chrome#n12` keeps the swap tile after the bubbles in the focus order (2026-11-25).** The tile sits at the bottom of the screen beside the orb, below the genre chips and the bubble field, so the current order follows the visual reading order, as WCAG 2.4.3 (Focus Order) asks. Moving it first would make focus jump from the search bar to the bottom and back.

**Findings of 4.1, 4.3 and 4.4 closed without a code change (2026-11-25), with the reason for each.**
- `tickets-and-virtual-ticket#n8` (the ticket face is not a tab stop): the Flip button is the face's keyboard control, next to it; a second tab stop for the same action would only add a stop.
- `cards-and-lists#1` (a list item of three or more lines stays centred): CSS cannot tell how many lines a wrapped supporting text takes, and the list item has no caller whose supporting text wraps past two lines today; revisit when one does.
- `chips#n5` (a long artist list scrolls inside a fixed box): M3 says to "consider" a horizontal scroll; a fan follows a handful of artists, and the box keeps the sheet's buttons in view.
- `snackbar#n5` (no shortcut to focus a snack): a snack with an action stays 10 s and pauses while focused (D5); a global shortcut is a new interaction with no M3 requirement behind it.
- `my-artists#n7` (arrow keys do not move between rows): each row is one radio group, so Tab moves between rows and the arrows move within one, as the ARIA radio group pattern prescribes.
- `my-artists#n0` (a dot's level name is only in the column header): the dots form a table whose column header names the level, and each radio is named "artist, level" for assistive technology.
- `progress-and-loading#n3` (a busy button's spinner has no role): the button carries `aria-busy="true"` and keeps its readable label; the spinner is decoration.
- `bottom-sheet#n6` (the sheet body shows no focus ring): the handle is now a button with the global ring (3.2), and the body receives focus only to start the trap, as the bottom-sheet spec's focus requirement states.
- `accessibility-and-reduced-motion#n6` (inline links are not 48 dp tall): M3 says to "consider" it; standalone links have 48 px (`text-link`), and inline links in running text are the usual exception.

**`buttons#6` lets a button's label wrap (2026-11-25).** M3 asks for a single-line label and concise strings. A button whose width its container sets (the concert sheet's out-of-range action and official-site link, stretched in a card) holds a label with a prefecture name in it; on a 320 px phone the English "Also get new concerts around Kanagawa" and the Japanese 「神奈川周辺の新着ライブも受け取る」 are wider than the button. Kept on one line they ran past the card, so the label wraps, which keeps it readable; the strings are the place to keep it short. A first attempt (932eca79) set `white-space: nowrap` on every button and was reverted after review on PR 1115.

**The findings that conflict with a living requirement, decided after reading each requirement's reason (2026-11-25).**
- `dialogs#n2` is adopted: the iPhone home-screen step's one action becomes 「わかった」, which acknowledges the message (the steps are done in the browser); the post-signup-dialog requirement is amended.
- `fab-and-action-menu#n2` is adopted in part: focus now stays on the FAB, the close control, when the arc opens (the M3 FAB menu and the disclosure pattern), and Tab reaches the panel next; the action-menu requirement is replaced. The items keep their order, nearest the FAB first, which follows the arc a thumb travels; reversing it would make Tab run against that path.
- `dialogs#n4` keeps the notification failure as a line in the sheet: the sheet is itself the dialog, and a second dialog over it would stack dialogs; the line says what failed and what to do.
- `fab-and-action-menu#n6` keeps the equalizer glyph: it is part of the brand, which the proposal keeps out of scope.
- `navigation-bar#n6` keeps the bar at 64 px: the FAB's notch is cut from the bar's height, and the tab labels are two to four characters.

**Task 4.5, measured (2026-11-25, Chromium, the resolved tokens).** The text field's border (`outline`, white at 22%) measured 1.93:1 on `surface` and 1.98:1 on `surface-container`; `outline` is now opaque `oklch(62% 0.02 275deg)`, 3.74:1 to 5.13:1 on every surface tier. The onboarding progress track's edge (white at 14%) measured 1.47:1; at 35% it is 3.21:1, and the band against the track measures 3.14:1. An outlined chip's or button's border (`outline-variant`) measures 1.36:1, which stays: the label identifies the control (WCAG 1.4.11), and M3's own `outline-variant` is decorative. The banners' message measures 11.8:1 to 18.1:1 through the 85% surface. The coach mark's tip was not reachable by a screen reader; the target now names it as its description. `tickets-and-virtual-ticket#n16` (the ticket's headline on its artwork) stays out of scope: the proposal keeps the virtual ticket unchanged, and the artwork differs per ticket.

**Task 3.2's findings beyond the eight that 524feb45 adopted, closed with their reasons (2026-11-25).**
- `navigation-bar#n3`, `timetable#n3`, `tickets-and-virtual-ticket#n7` (no ripple from the touch point): the app-shell requirement "Press is acknowledged by a state layer and shape morph" answers a press with a state layer keyed off the pressed state in stylesheets, so it costs nothing until a press and adds no per-control work; a ripple has to be placed at the touch point by a script for each press, which this task's own check ("no per-control script was added") rules out. The press is still acknowledged within the short motion band.
- `navigation-bar#n4` (the state layer takes the tab's content colour): the M3 web tokens in the snapshot give `on-surface` for every navigation bar item's state layer (`md.comp.navigation-bar.{active,inactive}.{hover,focus,pressed}.state-layer.color`), not `on-secondary-container` as the finding says; the app keeps its one rule, a state layer in the control's content colour, which differs from `on-surface` only in hue on the selected tab.
- `icon-buttons#n1` (a selected toggle is shown by colour alone): the selected toggle now also changes shape, to a 12 px rounded square (`icon-buttons#0`, 524feb45), so colour is no longer the only cue.
- `foundations-tokens-states#3` (no 0.38 disabled state layer): M3's disabled look is not a state layer but content at 38% and a container at 12%, which the controls apply themselves (`button.css`, `chip.css`, `text-field.css`, `menu.css`).

### Bottom sheet entry: the slide runs in a clipping box (2026-11-25)

A transform on the sheet body inside the scroller adds its travel to the scroll range, so the snap to the sheet landed one sheet-height too high and the sheet appeared near the top, then sank back. The slide now runs inside `sheet-surface`, which is a block box with `overflow: clip`; the DOM structure scenario of the bottom-sheet spec is modified accordingly. `overflow-clip-margin` (to keep the level 1 shadow's 3 px above the sheet) widens the scroll range by that margin during the slide, so it is not used: the top shadow edge is clipped, which is not visible against the 60 % backdrop. `RisesFromTheBottom` steps the animation and asserts the sheet never lies above its rest position and the scroll range does not change.

### Navigation bar selected icon: keep the outline (owner decision, 2026-11-26)

`navigation-bar#n1` and `#n2` (a filled icon for the selected tab, and an outline-to-filled transition) are not adopted. A story prototype filled the selected icon: the home icon and the search icon read well, but the music note and the ticket, drawn as strokes, lose their shape when filled (the ticket's notches and dashes disappear). Adopting it would need four new filled icons and a switch animation; the owner chose to keep the outline icon on every tab, since the selected tab already shows by colour, shape (the rounded container) and the emphasized label. `navigation-bar#n1` and `#n2` are closed with this reason.

### Tab switch frame rate (2026-11-26)

The owner tried the tab switch on the Android test device after the fade-only transition and found no dropped frames worth acting on; the opacity-only fallback in Risks is not needed.

### Spec corrections before the archive (owner agreed, 2026-11-26)

A check of the delta specs against the shipped code found places where one of them was wrong. The code gained what was missing (fade-in on the concert page and the entry screens, skeletons for the search and the delete-account blockers, a fade for the Discovery swap under reduced motion, the install banner hidden rather than destroyed, the month-jump fade). The specs now state: first screen without animation and later redirects as ordinary screen changes; the places that change at once under reduced motion (an instant change reads better than a fade for a disclosure, an in-place edit, the month jump and a sheet's close; a progress indicator must keep moving); approximate skeleton sizes where the height follows the data (D11); the Japanese line height by app language.
