## MODIFIED Requirements

### Requirement: PWA Install Prompt i18n

The PWA install prompt SHALL use i18n keys for all user-facing text, consistent with the notification prompt's existing i18n pattern.

#### Scenario: PWA install prompt displays localized text

- **WHEN** the PWA install prompt is visible
- **THEN** the title text SHALL be rendered via the `pwa.title` i18n key
- **AND** the description text SHALL be rendered via the `pwa.description` i18n key
- **AND** the install button label SHALL be rendered via the `pwa.install` i18n key
- **AND** the dismiss button label SHALL be rendered via the `pwa.notNow` i18n key
- **AND** the text SHALL NOT be hardcoded in the template

---

### Requirement: Prompt Entrance and Exit Animations

The PWA install prompt and notification prompt SHALL animate when entering and leaving the viewport, providing visual continuity with the rest of the onboarding flow.

#### Scenario: Prompt entrance animation

- **WHEN** the PWA install prompt or notification prompt becomes visible
- **THEN** the prompt SHALL animate in using a fade-slide-up effect (opacity 0 -> 1, translateY 16px -> 0)
- **AND** the animation duration SHALL be 600ms with ease-out timing
- **AND** the animation SHALL reuse the existing `fade-slide-up` keyframe defined in `my-app.css`

#### Scenario: Prompt exit animation

- **WHEN** the PWA install prompt or notification prompt is dismissed
- **THEN** the prompt SHALL animate out using a fade-slide-down effect (opacity 1 -> 0, translateY 0 -> 16px)
- **AND** the animation duration SHALL be 600ms with ease-out timing
- **AND** the element SHALL remain in the DOM until the exit animation completes

#### Scenario: Reduced motion preference

- **WHEN** the user has `prefers-reduced-motion: reduce` enabled
- **THEN** the prompt entrance and exit animations SHALL be skipped
- **AND** the prompt SHALL appear and disappear instantly
