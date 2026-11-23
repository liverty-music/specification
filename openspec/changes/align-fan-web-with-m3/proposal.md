## Why

The fan web app was built on Material 3 (M3) tokens, but its motion and several interaction details are older than the guideline. A static audit of the app (frontend `main` at `3e0cc066`) against the M3 guideline found 342 differences. 122 are worth adopting because the fan benefits, and 49 needed an owner decision (settled; see design.md). The most visible ones are: tab switches fade the old and the new screen at the same time, screens opened from inside a page appear with no motion, data loads show plain text instead of a placeholder shape, and Japanese text is set on the Latin line height. The owner wants the app to feel richer to use and accepts changing a spec where M3 serves the fan better.

## What Changes

- **Motion between screens.** A tab switch becomes M3's "top level" pattern (the old screen leaves quickly, then the new one enters). A screen opened from inside a page, and the way back, gets a short forward/backward motion. Under reduced motion the app keeps a subtle fade and stops decorative loops, instead of cutting instantly.
- **Enter and exit motion** for sheets, banners, menus, coach-marks and similar surfaces that now appear or disappear with no motion or only a fade.
- **Loading placeholders.** Content that loads shows a skeleton shape and fades in when it arrives, instead of a bare "Loading…" line or a sudden pop-in.
- **State feedback.** The toggle switch becomes 52 × 32 px and its handle grows while pressed (the one exception to "no control scales when pressed"); selected and pressed states on tabs, chips and the navigation bar are given the M3 feedback.
- **Snack bar.** A snack with an action keeps its 10-second display time but pauses while the fan hovers or focuses it.
- **Accessibility and forms.** Keyboard, screen-reader, text-size, 48 px touch-target, form-error and long-text fixes, listed in `audit-items.md`. This includes the Timetable concert card, which cannot be opened with the Enter key.
- **Japanese line height.** Japanese text takes M3's "medium" language height instead of the Latin (small) line height.
- **Out of scope, decided:** brand colours, shapes, typefaces and shadows stay; the 10-second action snack and the snack's severity icon stay; the bottom sheet keeps its non-dismissable scrim; wide-screen rail layouts are deferred; surfaces with no M3 counterpart (artist bubbles canvas, celebration, virtual ticket flip) are not changed.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `components/infrastructure/fan/web/global/app-shell`: tab switches use the top-level motion; screens opened from inside a page and the way back move; reduced motion keeps a subtle fade; a switch handle may grow while pressed.
- `components/infrastructure/fan/web/global/ui-primitives`: loading content shows a skeleton and fades in; confirmation dialogs keep a subtle fade under reduced motion, and disclosures still open at once.
- `components/infrastructure/fan/web/global/snack-bar`: a snack's display time pauses while the fan hovers over it or focuses it.
- `components/infrastructure/fan/web/global/design-tokens`: Japanese text takes the medium language height.
- `components/infrastructure/fan/web/route/settings`: the toggle switch size and press behaviour.

## Impact

- **Code:** frontend only (`src/` styles, route and component templates, the router transition hooks, the shared state-layer and token stylesheets). No backend, proto, database or infrastructure change.
- **Specs:** the five capabilities above. Findings whose spec states the current behaviour for a reason not yet checked (listed in design.md "Findings that need the spec's reason first") are amended through `/opsx:update` when apply reaches them.
- **Verification:** unit and component tests, visual baselines for changed components, Playwright flows against a local build and, after merge, the prod app. The dev environment is stopped, so no task needs it.
- **Source data:** `audit-items.md` in this change lists every finding by `ref` and theme.
