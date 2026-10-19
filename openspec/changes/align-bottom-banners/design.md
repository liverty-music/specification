## Context

The two banners live in `src/components/pwa-install-banner/` and `src/components/signup-prompt-banner/`. Each banner styles itself inside its own `@scope` block. Both put the shared `button` (`data-variant="on-container"`) on their surface, and both publish their height as `--bottom-banner-height` for the FAB and the snack bar. The code today:

| | install banner | signup prompt |
|---|---|---|
| surface | `oklch(11% 0.06 270deg / 95%)`, a 14%/7% brand tint wash, `blur(24px) saturate(180%)` | `oklch(18% 0.04 275deg / 85%)` (the value of `--color-surface-base`), `blur(12px)` |
| top line | `::before` 1.5px gradient, plus an `::after` glow bloom | `border-block-start: 2px` with a gradient `border-image` |
| offset | `calc(3.5rem + env(safe-area-inset-bottom, 0px))` | the same |
| CTA glow | `pwa-cta-pulse` 2.5s `infinite`, brand-primary | `cta-glow` 2.5s `infinite`, brand-primary |
| message | `--step--1`, 500, `--color-text-primary`, `opacity: 0.88`, one line with ellipsis | `--step-0`, 400, `--color-text-secondary`, wraps to two lines |
| entrance | `pwa-banner-enter`, `translateY(110%)` to 0, `--md-duration-medium3` (350ms), emphasized-decelerate | `banner-enter`, slide and fade, `400ms ease-out` |

The install banner spec also has two requirements no code meets. "PWA Install Prompt i18n" names `pwa.title`, `pwa.description`, `pwa.install` and `pwa.notNow`, but the banner takes its text from `pwaInstallBanner.*`, and nothing in `src/` reads those four keys (`main.ts` reads only `pwa.updateAvailable` and `pwa.updateAction`). "Prompt Entrance and Exit Animations" asks for the 600ms `fade-slide-up` / `fade-slide-down` utilities (`src/styles/utilities.css`) on the install banner and the notification prompt. The notification prompt has no animation, and the install banner is removed by `if.bind` with no exit animation.

The snack's attention glow is `snack-action-glow 1.2s ease-in-out 3` (`shared/ui/snack-bar/snack-bar.css`). Neither banner has a story, so axe has never checked either of them.

## Goals / Non-Goals

**Goals:**
- One surface, offset, glow and message text for both banners, written in each banner's own block and pinned by a test.

**Non-Goals:**
- Changing the snack bar, the shared button, either banner's layout (the install banner's single row and the signup prompt's column) or the message sizes, which follow those layouts.

## Decisions

### D1. The signup prompt's surface becomes the shared banner surface

Both banners use `background: oklch(from var(--color-surface-base) l c h / 85%)`, `backdrop-filter: blur(12px)`, and `border-block-start: 2px solid` with `border-image: linear-gradient(to right, var(--color-brand-primary), var(--color-brand-secondary)) 1`. The install banner drops its own base colour, the tint wash, the `::before` line and the `::after` bloom. These are the values both specs already state ("dark base at about 85% opacity", "2px gradient"). The signup prompt meets them, and the install banner had drifted from them.

*Alternative:* keep the install banner's richer surface and copy it to the signup prompt. Rejected: that changes the spec instead of meeting it, and the bloom and the tint are the parts that drifted.
*Alternative:* a shared `bottom-banner` block or utility class in `src/styles/`. Rejected for now: two components share four declarations. A story check on each banner (D4) catches drift at lower cost than adding a new block to the CUBE layers.

### D2. The CTA glow plays three times with the snack's timing

Each banner's existing keyframes keep their brand-primary shadow (white is the snack's glow on its coloured fill; a banner's glow sits on a dark surface). The animation becomes `1.2s ease-in-out 3`, inside the existing `prefers-reduced-motion: no-preference` query. It starts when the banner is inserted (`if.bind`), which is when the banner becomes visible.

*Alternative:* keep 2.5s and only limit the count. Rejected: the specs ask for the snack's timing so that every bottom surface's attention cue reads the same.

### D3. Offset and message text

`inset-block-end: calc(var(--bottom-nav-height) + env(safe-area-inset-bottom, 0px))` replaces the hard-coded `3.5rem` (the token is `3.5rem` today, so nothing moves). Both messages use `color: var(--color-text-primary)` and `font-weight: 500`. The install banner drops `opacity: 0.88`, which lowered contrast by an amount that depends on what lies under the banner.

### D4. Stories for both banners, with the snack's contrast helpers shared

`src/components/signup-prompt-banner/signup-prompt-banner.stories.ts` renders the banner with `visible` and a message. `src/components/pwa-install-banner/pwa-install-banner.stories.ts` uses `defineAureliaStory` with a mock `IPwaInstallService` registered through `items`, as the project's Storybook rules allow for DI-bound components. Each story asserts:
- the computed background equals the resolved `oklch(from var(--color-surface-base) l c h / 85%)`, the top border is 2px, and no `linear-gradient` is in `background-image` (the surface is not a gradient fill);
- `inset-block-end` equals the resolved navigation height plus the safe area;
- the message colour equals `--color-text-primary` and its weight is 500;
- the message reaches 4.5:1 against the surface composited over both the page background and white (white is the worst case for content seen through the translucent surface);
- the CTA's animation has an iteration count of 3 and ends in `finished`; under reduced motion it has none;
- the entrance animation lasts 350ms and starts from `opacity: 0`; under reduced motion the banner has no entrance animation;
- the install banner's texts equal the Japanese translations (the stories' i18n is Japanese), and the signup prompt shows the bound message and offers no dismiss control.

The contrast helpers in `shared/ui/snack-bar/snack-bar.stories.ts` (`resolveColor`, `composite`, `contrast`) move to `.storybook/contrast.ts`, so that the snack and the banner stories share one implementation.

*Alternative:* assert in Playwright e2e only. Rejected: the e2e reaches each banner only through sign-up or onboarding state. Stories render them directly and also put them under the axe check.

### D5. One entrance on the motion token, and the stale requirements

Both banners use one entrance: `translateY(100%)` and `opacity: 0` to rest, over `var(--md-duration-medium3)` with `var(--md-easing-emphasized-decelerate)`, inside `prefers-reduced-motion: no-preference`. The token is 350ms and collapses to 0ms under reduced motion (`shared/styles/m3-sys.css`). The specs state 350ms instead of 400ms. The token is what the install banner already uses, and the M3 motion scale is the app's shared vocabulary.

"PWA Install Prompt i18n" is restated around what the user sees, not the key names, so that renaming a key is not a spec change. "Prompt Entrance and Exit Animations" is removed rather than implemented. An exit animation would keep a hidden banner in the DOM and its buttons in the tab order, against "Banner is removed from DOM when hidden". The four unused `pwa.*` keys are deleted from both locales; `pwa.updateAvailable` and `pwa.updateAction` stay.

*Found during apply:* both banners put their entrance on the host element (`:scope`), which stays mounted while the banner is hidden, so the entrance played when the page mounted the host, not when the banner appeared. The entrance now sits on the banner itself (`.pwa-banner`, `.signup-banner`), which `if.bind` inserts when it shows, as the specs' "becomes visible" asks.

*Alternative:* implement the removed requirement. Rejected for the reason above, and because the notification prompt is not a bottom banner and has never animated.

## Risks / Trade-offs

- **[The install banner looks plainer without the bloom and tint]** → It now matches the signup prompt and its own spec, and the user chose to tell banners apart from snacks by role rather than by decoration. Compare the two stories in Storybook before merging.
- **[A glow that stops is easier to miss]** → The banner itself stays until the user acts or dismisses it, so a continuous cue adds little. The snack already uses the same three-time pattern.
