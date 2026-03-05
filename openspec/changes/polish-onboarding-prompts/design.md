## Context

The onboarding flow uses spring easing, staggered fade-slide-up, and layered effects throughout the tutorial steps. However, three key UI elements -- the PWA install banner, the notification prompt, and the sign-up modal -- appear and disappear instantly with no animation. This visual inconsistency makes the prompts feel mechanical and disruptive compared to the polished tutorial flow.

Additionally, the PWA install banner has hardcoded English text (no i18n support), and the Step 5 Passion Level explanation has a 3-second silent delay before appearing, leaving the user waiting with no visual feedback that their tap registered.

The existing codebase already defines a `fade-slide-up` keyframe in `my-app.css` (opacity 0 -> 1, translateY 16px -> 0) and a `prefers-reduced-motion` media query that disables all animations.

## Goals / Non-Goals

### Goals

- Unify entrance/exit animation style across all onboarding prompts and modals.
- Localize PWA install banner text via i18n keys.
- Reduce perceived latency on Step 5 passion explanation by providing immediate tap feedback and shortening the delay.

### Non-Goals

- Changing prompt display logic or sequencing (that belongs to a separate change controlling when prompts appear).
- Changing prompt content beyond adding i18n key references for the PWA banner.
- Redesigning the sign-up modal layout or content.
- Adding new animation infrastructure -- reuse existing keyframes and the `prefers-reduced-motion` guard.

## Decisions

### Decision 1: Reuse `fade-slide-up` for prompt entrance; add `fade-slide-down` for exit

The `fade-slide-up` keyframe already exists in `my-app.css` with `translateY(16px) -> 0` and `opacity 0 -> 1`. Both the notification prompt and the PWA install prompt will use this keyframe for entrance animation at 600ms with ease-out timing.

A corresponding `fade-slide-down` keyframe will be added for exit animations (`translateY(0) -> 16px`, `opacity 1 -> 0`). Both keyframes are wrapped in the existing `prefers-reduced-motion` guard.

The prompts will be wrapped in a container element that triggers the animation class on Aurelia's `if.bind` mount/unmount cycle, ensuring animations play each time the prompt appears or is dismissed.

### Decision 2: Sign-up modal uses scale + fade entrance with radial glow

The sign-up modal entrance will use `scale(0.95) -> scale(1)` combined with `opacity 0 -> 1` over 400ms with cubic-bezier spring easing (`cubic-bezier(0.34, 1.56, 0.64, 1)`), matching the Discover HUD style already used in the onboarding flow.

A subtle radial gradient glow will be added behind the modal content panel using a CSS pseudo-element (`::before`) with the brand-primary color at low opacity, providing a warm highlight effect consistent with the `--shadow-card-glow` token used elsewhere.

### Decision 3: PWA banner i18n keys under `pwa.*` namespace

All hardcoded English text in the PWA install prompt template will be replaced with i18n key references using Aurelia's `t` binding attribute. The keys follow the existing namespace convention (e.g., `notification.*` for the notification prompt):

| Key               | English value                                                        |
|--------------------|----------------------------------------------------------------------|
| `pwa.title`        | Add to Home Screen                                                   |
| `pwa.description`  | Install Liverty Music for faster access and offline browsing.        |
| `pwa.install`      | Install                                                              |
| `pwa.notNow`       | Not now                                                              |

Keys must be added to all supported locale files under `frontend/src/locales/`.

### Decision 4: Step 5 passion explanation -- immediate feedback + 800ms delay

The current 3000ms `setTimeout` in `my-artists-page.ts` (line 336-341) will be reduced to 800ms. Before the timeout fires, an immediate visual feedback animation will play on the passion button the user tapped -- a brief highlight/pulse effect (scale 1 -> 1.1 -> 1 over ~300ms) -- confirming the selection registered. This eliminates the 3-second "dead zone" where nothing visually responds to the user's action.

The explanation modal itself appears after 800ms, giving just enough time for the pulse to complete before the next piece of UI appears.

## Risks / Trade-offs

### Animation on `if.bind` unmount timing

Aurelia's `if.bind` removes elements from the DOM immediately when the condition becomes false. Exit animations require the element to remain in the DOM during the animation. This will need either:
- Using `au-animate` with the Aurelia animation plugin, or
- Using `show.bind` (which toggles `display` rather than removing from DOM) with CSS animation classes, or
- A wrapper component that delays DOM removal until the exit animation completes.

The simplest approach is `show.bind` with CSS animation classes toggled via a state property, but this keeps the element in the DOM at all times. Given these are lightweight prompt elements, the DOM cost is negligible.

### Reduced-motion compliance

All new animations must be covered by the existing `@media (prefers-reduced-motion: reduce)` rule in `my-app.css`. The current rule targets `[class*="animate-"]` selectors. New animation classes must follow this naming convention or be explicitly added to the media query.

### 800ms delay may still feel slow on fast interactions

The 800ms delay is a compromise. Shorter delays risk the explanation modal appearing before the user has processed the passion level change. The immediate pulse animation bridges the gap, but user testing may reveal a need to adjust.
