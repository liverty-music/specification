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

**D3. Reduced motion keeps a short fade (100 ms or less) and stops movement.** M3: "subtle fades instead of intense sliding". Decorative loops (shimmer, pulsing, spinning decoration) stop. Alternative: stay instant (rejected: an instant swap is a jump cut, which the guideline lists as jarring).

**D4. The toggle switch becomes 52 × 32 px with a handle that grows on press; this is a stated exception to "no control scales when pressed".** The numbers (track 52 × 32, handle 16 unselected, 20 default, 24 selected, 28 pressed) are the M3 switch tokens (`tokens/md-comp-switch.md`). With the current 44 × 24 track a 28 px handle would not fit, so size and press behaviour are decided together. The activation target stays as the Settings spec states (at least 24 px on both axes, with the adjacent disclosure control as the larger neighbouring target); the larger track already meets it.

**D5. A snack with an action stays 10 s, and its timer pauses while the fan hovers or focuses it.** M3 says action snackbars should not auto-dismiss. The project's snack-bar spec sets 10 s for a snack with an action (the Snack Bar Component requirement), and a snack that never leaves would stay over the bottom navigation on a phone; the owner kept 10 s. Pausing while the fan is interacting removes the real harm (the snack leaving while it is being read or used).

**D6. The snack's severity icon stays.** It tells the severity without colour. M3 does not forbid it.

**D7. The date tabs are treated as a segmented button, not as tabs.** They select one of a few dates in place and do not switch content areas. This settles `K8` findings about tab placement and indicators; those findings are then checked against the segmented-button guidance instead.

**D8. Japanese text takes the medium language height.** M3: "default to medium language height… switch to other sizes based on detected language", and ignoring it risks overlapping text. The snapshot proves one value (display-large: 64 px small, 73 px medium); the others are in Open Questions. The earlier "about 7% taller" estimate was wrong and is not used.

**D9. The bottom sheet's scrim stays non-dismissable, and wide-screen rails wait.** The bottom-sheet spec requires the scrim not to close the sheet, to stop accidental loss of a half-filled form. Wide screens are not the fan app's use (phone first).

**How the motion is built.** Screen changes go through the app's existing route-transition hooks, which already use the browser's View Transitions; the change adds a per-navigation kind (tab switch, forward, back) so the right pattern runs. Enter and exit motion uses CSS (`@starting-style` and `transition-behavior: allow-discrete`) for elements that are shown and removed, with durations and easing taken from the motion tokens (no raw milliseconds). Skeletons are one shared presentational piece in the shared styles, reused by each screen, so a screen declares only what its placeholder looks like. Press and selected feedback stays in stylesheets keyed off state, in line with the existing "no per-control work" rule in the app-shell spec.

**Findings that need the spec's reason first.** Six adopt findings conflict with a requirement that says why it exists: `dialogs#n2`, `dialogs#n4` (post-signup dialog steps), `fab-and-action-menu#n2`, `fab-and-action-menu#n6` (action menu order and behaviour), `discovery-chrome#n13` (discovery reduced motion) and `welcome-onboarding-celebration#n0` (welcome reduced motion). Apply reads each requirement's rationale first. If M3 still serves the fan better, the spec is amended through `/opsx:update` before the code changes; if the rationale holds, the task is closed with the reason written beside it.

## Risks / Trade-offs

- [A new top-level transition adds a View Transition on every tab tap, which could cost frames on low-end phones] → measure on the Android test device before and after; the 200 ms ceiling and a fade-only transition keep the cost low. If it drops frames, fall back to an opacity-only CSS fade without View Transitions.
- [Skeletons that do not match the loaded layout make the page jump when content arrives, which is worse than the loading text] → each skeleton takes the exact size of the loaded rows; a visual baseline compares the two states.
- [Medium line height changes every Japanese screen's height and can push content off screen or break fixed-height components] → apply the token change, then check each screen with the visual baselines and the audit's text-size and long-string findings (`T13`) in the same pass.
- [The audit was static, so some findings may not reproduce] → each fix task starts by reproducing the finding on the local build; a finding that does not reproduce is closed with that note, not changed.
- [Reduced-motion fades are new motion for people who asked for less] → they are 100 ms or less and have no movement, as M3 states.

## Open Questions

- The medium line height of every type style except display-large (73 px). Task 5.1 reads them from the official type scale and adds them to the `design-tokens` spec table through `/opsx:update` before the code is changed. Until then the small value applies to the other styles, which the spec states.
- Whether the navigation bar's selected icon should be a filled version (`K10`) and how switch and nav-bar feedback should look beyond the switch. The owner has not chosen; section 3 treats the nav-bar icon as a decision to take on a prototype on the Android test device, not as a task to implement now.
