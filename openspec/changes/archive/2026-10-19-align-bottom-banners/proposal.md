## Why

The fan app shows three surfaces above the bottom navigation: the snack bar, the install banner and the signup prompt. They differ in ways no spec decides. The snack bar is a brand-gradient fill. The two banners are a dark surface with a brand line, but each banner sets that surface with its own values. The install banner's surface no longer matches its own spec (a 95% base with a 1.5px line and a glow, where the spec says about 85% with a 2px border). The banners' action glows forever, while the snack's attention glow plays three times and stops. The banners hard-code `3.5rem` for the navigation's height, and their messages use different colours and weights. In `snack-text-contrast` the user chose the filled gradient for the snack over a dark surface with a brand stripe. So the snack and the banners now look like two systems, with nothing that says whether that is intended.

## What Changes

- The difference is made intentional and written down, by role. A snack is transient and filled with the brand gradient, as now. A banner is persistent and sits on the dark surface with a 2px brand-gradient top line. A banner SHALL NOT use the snack's filled gradient.
- Both banners use the same surface: the surface-base colour at 85% opacity with backdrop blur, and the 2px brand-gradient top border. The install banner drops its own 95% base, its tint wash, its 1.5px line and its glow bloom.
- The banners' action glow plays three times when the banner appears and then stays still, with the snack's attention timing. It no longer pulses for as long as the banner is shown. With reduced motion there is no glow, as now.
- Both banners sit at the navigation's height token (`--bottom-nav-height`) plus the safe area, instead of a hard-coded `3.5rem`.
- Both banners' messages use the primary text colour at weight 500, without the install banner's 88% opacity.
- Both banners slide up and fade in over the app's medium motion duration (350ms). Today the install banner slides without a fade over 350ms, and the signup prompt slides and fades over 400ms. Both specs say 400ms.
- The install banner spec's stale requirements are corrected. "PWA Install Prompt i18n" names translation keys of an earlier prompt (`pwa.title`, `pwa.description`, `pwa.install`, `pwa.notNow`); it now states the banner's own text. "Prompt Entrance and Exit Animations" (a 600ms fade in and out, keeping the element in the DOM until the exit ends) is removed: it contradicts the banner's entrance and its removal from the DOM when hidden, and no code meets it. The four unused `pwa.*` translation keys are deleted.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `components/infrastructure/fan/web/global/pwa-install-banner`: "Banner Visual Presentation" states the role, the shared surface, the token offset, the glow that stops, the message text and the 350ms entrance. "PWA Install Prompt i18n" states the banner's own text. "Prompt Entrance and Exit Animations" is removed.
- `components/infrastructure/fan/web/global/signup-prompt-banner`: "Shared Banner Component" states the same surface, offset, glow, message text and entrance.

## Impact

- **frontend only.** No proto, backend or infrastructure change.
- `src/components/pwa-install-banner/pwa-install-banner.css` and `src/components/signup-prompt-banner/signup-prompt-banner.css`.
- `src/locales/{ja,en}/translation.json` (the unused `pwa.title`, `pwa.description`, `pwa.install` and `pwa.notNow` keys).
- New Storybook stories for both banners (`src/components/<name>/<name>.stories.ts`), which also put the banners under the axe contrast check for the first time.
- The snack bar is unchanged.
