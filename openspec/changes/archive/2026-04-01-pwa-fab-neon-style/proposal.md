## Why

The PWA install FAB is easy to miss. The icon is small (1.25rem / 20px) and the idle glow is static — it lacks the visual energy of other CTAs in the app such as the signup banner. Enlarging the icon and adding a pulsing neon border brings the FAB in line with the app's neon aesthetic and makes it more noticeable without adding new UI elements.

## What Changes

- Increase the FAB icon size from `1.25rem` to `1.5rem`
- Replace the static idle `box-shadow` glow with a `2.5s ease-in-out infinite` pulsing neon animation (matching the `cta-glow` pattern from `signup-prompt-banner`)
- The pulse uses an inset spread-radius layer (`0 0 0 2px`) to simulate a neon border, since `border-image` is incompatible with `border-radius: full`
- Color tokens remain: `--color-brand-primary` and `--color-brand-accent` (existing `--_glow-color-from` / `--_glow-color-to` variables)

## Capabilities

### New Capabilities
<!-- none -->

### Modified Capabilities
- `pwa-install-fab`: Idle state gains pulsing neon border animation; icon rendered larger

## Impact

- `frontend/src/components/pwa-install-fab/pwa-install-fab.css` — CSS-only change
- No TypeScript, HTML, or test changes required
- No API or backend changes
