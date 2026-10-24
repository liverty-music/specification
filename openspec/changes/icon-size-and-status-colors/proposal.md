## Why

The fan web's icons and status colors break silently (frontend#841). The 2026-10-24 prod walk-through of fan-email-verification-in-app turned up several:

- **Size set on an icon is ignored.** Seven places set a size on `<svg-icon>` that never applies, because the component sizes its inner SVG from a private value. The `/verify-email` check rendered at 1.25rem instead of 3.75rem.
- **A missing icon shows as "!".** An unknown icon name renders a "!" circle instead of nothing, so the missing `mail` icon in Settings looked like a warning.
- **One meaning, several colors; two meanings, one color.** "Done" is drawn in four colors, one of them an undefined token (`--color-accent`, so the verify-callback success icon has no color). "Selected" borrows the success green in Discovery. The success green (hue 152°) sits 12° from the brand accent green (hue 140°), so a fan cannot tell "brand" from "done".

## What Changes

- **Icon size follows the text.**
  - An icon is as large as the text around it (`1em`) unless it is given a size.
  - The `size` steps (xs to xl) and a stylesheet's size both take effect.
  - **BREAKING (visual)**: icons that relied on the 1.25rem default inside smaller or larger text change size.
- **An unknown icon name renders nothing**, as the spec already requires. The `mail` icon joins the required set.
- **Status colors are named by meaning.**
  - Done/verified uses the success color.
  - Selected uses the primary (brand pink).
  - Warning and error keep their tokens.
  - Every status color resolves to a defined token.
- **The success color is moved away from the brand accent.** It stays green (ticket PAID keeps "a success color (green)"), and it is far enough from the accent and the stage colors to be told apart.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `components/infrastructure/fan/web/global/ui-primitives`: SVG Icon Component.
  - The default size follows the surrounding text.
  - A size set by the `size` attribute or by a stylesheet applies.
  - The required icon set gains `mail`.
  - The unknown-name rule (render nothing) is unchanged, and is now honoured.
- `components/infrastructure/fan/web/global/design-tokens`: a new requirement for status colors by meaning (done, selected, warning, error). The success color must be distinguishable from the brand accent and the stage colors.

Unchanged and relied on: `components/infrastructure/fan/web/global/event-detail-sheet` "Ticket Status semantic color and non-color cues". PAID still uses the success color, which stays green.

## Impact

- **frontend**:
  - `svg-icon` sizing and fallback.
  - The success token value.
  - The call sites listed in design (seven sizes, four status colors).
  - A stylelint check for undefined `--color-*` tokens.
  - Updated Storybook baselines (`svg-icon`, `state-placeholder`, `page-header`, `inline-error`, `button`, `snack-bar`, `event-date-tabs`) where icon size or success color shows.
- **backend, cloud-provisioning, proto**: none.
