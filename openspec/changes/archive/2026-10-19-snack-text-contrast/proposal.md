## Why

The fan app's snack bars put white text on bright gradients that fall short of WCAG AA (4.5:1). The info message measures 3.66 to 3.88:1 on the brand gradient, and the warning message drops to 4.03:1 at the gradient's light end. The update snack's compact action, made smaller in `unify-fan-buttons-and-center-fab` so that the message fits one line, is no longer large text: it measures 3.06 to 3.35:1 on info and 3.05 to 3.57:1 on warning. That change's design records this as a known gap and leaves the fix to this change.

## What Changes

- The info snack keeps the brand hues and chroma, and its gradient is darkened: brand-primary's hue at oklch lightness 50.5%, brand-secondary's at 48%.
- The warning snack keeps its amber hue and chroma at lightness 47.5% on both stops.
- With these colours, the white message and the update snack's compact on-container action both reach 4.5:1 at every point of the gradient, including mid-way, where the blend of the two hues is darkest for the action. The error snack already passes and is unchanged.
- The colours are derived inside the snack bar from the brand tokens. The brand tokens and every other brand surface stay as they are: the FAB fill, the navigation's top line and the filled button.
- The organizer console's snack bar sets its own container colour and is unaffected.

The user chose darkening the gradients after comparing three options in Storybook: the darker gradients, a neutral dark surface with a brand stripe, and the current gradients with 19px bold text. The large-text option wrapped the update message at 360px again.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `components/infrastructure/fan/web/global/snack-bar`:
  - The severity variants describe darkened info and warning gradients instead of the plain brand gradient.
  - A new requirement sets 4.5:1 as the minimum for the snack's text and action on every severity.

## Impact

- **frontend only.** No proto, backend or infrastructure change.
- `shared/ui/snack-bar/snack-bar.css` (info and warning gradient stops).
- `shared/ui/snack-bar/snack-bar.stories.ts` (contrast assertions along each gradient; the severity stories gain an action; the UpdateAction screenshot changes, the only snack story with a baseline).
